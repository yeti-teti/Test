from flask import Flask, render_template,jsonify,request, session
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from src.helper import download_hugging_face_embeddings
from src.prompt import *
from src.mcp_client import get_mcp_client
import os
import uuid
import re
from typing import Optional, Dict

app= Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

load_dotenv(".env")
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT")


PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
# OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

## Setup retriever
embeddings=download_hugging_face_embeddings()
index_name="medicalbot"

from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from typing import List

pc_client = Pinecone(api_key=PINECONE_API_KEY)
pc_index = pc_client.Index(index_name)

class DirectPineconeRetriever(BaseRetriever):
    index: any
    embeddings: any
    k: int = 3
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """Get documents relevant to a query using direct Pinecone query."""
        # Get query embedding
        query_vector = self.embeddings.embed_query(query)
        
        # Query Pinecone directly
        results = self.index.query(
            vector=query_vector,
            top_k=self.k,
            namespace='default',
            include_metadata=True
        )
        
        # Convert to LangChain documents
        documents = []
        for match in results['matches']:
            metadata = match.get('metadata', {})
            content = metadata.get('text', '')
            documents.append(Document(
                page_content=content,
                metadata=metadata
            ))
        
        return documents

retriever = DirectPineconeRetriever(index=pc_index, embeddings=embeddings, k=3)

# Also keep the vector store for potential other uses
docsearch=PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
    namespace="default",
    text_key="text"
)

# Global chain storage for conversational memory
chains = {}

def get_or_create_chain(session_id):
    """Get or create a conversational chain for the session."""
    if session_id not in chains:
        chains[session_id] = build_conversational_rag_chain(retriever)
    return chains[session_id]

# === Small talk handler ===
def handle_small_talk(msg: str):
    msg_lower = msg.lower().strip()
    greetings = ["hi", "hello", "hey"]
    farewells = ["bye", "exit", "quit", "goodbye"]
    thanks = ["thanks", "thank you"]

    if any(word in msg_lower for word in greetings):
        return "Hello! How can I help you with a medical question today?"
    elif any(word in msg_lower for word in farewells):
        return "Goodbye! Stay healthy."
    elif any(word in msg_lower for word in thanks):
        return "You're welcome! Do you have another medical question?"
    return None

# === Ingestion intent detection ===
def detect_ingestion_intent(msg: str) -> Optional[Dict[str, str]]:
    """
    Detect if user wants to ingest a dataset.
    Returns dict with file_path and format_type if detected, None otherwise.
    """
    msg_lower = msg.lower().strip()
    
    # Patterns that indicate ingestion intent
    ingestion_patterns = [
        r"ingest\s+(?:dataset|data|file)?\s*(?:from|at|:)?\s*(.+)",
        r"add\s+(?:dataset|data|file)\s+(?:from|at|:)?\s*(.+)",
        r"load\s+(?:dataset|data|file)\s+(?:from|at|:)?\s*(.+)",
        r"import\s+(?:dataset|data|file)\s+(?:from|at|:)?\s*(.+)",
        r"upload\s+(?:dataset|data|file)\s+(?:from|at|:)?\s*(.+)",
        r"use\s+(?:dataset|data|file)\s+(?:from|at|:)?\s*(.+)",
    ]
    
    # Also check for list datasets requests
    if any(keyword in msg_lower for keyword in ["list datasets", "show datasets", "list files", "what datasets", "list dataset"]):
        return {"action": "list"}
    
    for pattern in ingestion_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            file_path = match.group(1).strip()
            
            # Clean up common phrases and quotes
            file_path = re.sub(r'\s+(?:from|at|in|the|a|an)\s+', ' ', file_path)
            file_path = file_path.strip('"\'`')
            
            # Detect format from extension
            format_type = "auto"
            if file_path.endswith('.json'):
                format_type = "json"
            elif file_path.endswith('.csv'):
                format_type = "csv"
            elif file_path.endswith('.pdf'):
                format_type = "pdf"
            
            return {
                "action": "ingest",
                "file_path": file_path,
                "format_type": format_type
            }
    
    return None

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/ask", methods=["POST"])
def ask():
    msg = request.json.get("query")  # expecting JSON {"query": "..."}

    # Ensure session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    session_id = session['session_id']

    smalltalk_reply = handle_small_talk(msg)
    if smalltalk_reply:
        return jsonify({"answer": smalltalk_reply, "sources": []})

    ingestion_info = detect_ingestion_intent(msg)
    if ingestion_info:
        try:
            mcp_client = get_mcp_client()
            
            if ingestion_info.get("action") == "list":
                result = mcp_client.list_datasets()
                if result.get("success"):
                    datasets = result.get("datasets", [])
                    if datasets:
                        answer = f"📊 Found {len(datasets)} ingested dataset(s):\n\n"
                        for ds in datasets:
                            answer += f"• **{ds['name']}** ({ds['format']}, {ds['record_count']} records)\n"
                        answer += "\nNote: These datasets are tracked by MCP. To make them searchable, run 'python store_index.py'."
                    else:
                        answer = "No datasets have been ingested yet. Use 'ingest dataset <filename>' to add one."
                    return jsonify({
                        "answer": answer,
                        "sources": [],
                        "ingestion_result": result
                    })
                else:
                    return jsonify({
                        "answer": f"❌ Error listing datasets: {result.get('error', 'Unknown error')}",
                        "sources": []
                    })
            
            elif ingestion_info.get("action") == "ingest":
                file_path = ingestion_info.get("file_path")
                format_type = ingestion_info.get("format_type", "auto")
                
                result = mcp_client.ingest_dataset(file_path, format_type)
                
                if result.get("success"):
                    metadata = result.get("metadata", {})
                    answer = (
                        f"✅ Successfully ingested dataset '{metadata.get('name', 'unknown')}'!\n\n"
                        f"📊 Details:\n"
                        f"- Format: {metadata.get('format', 'unknown')}\n"
                        f"- Records: {metadata.get('record_count', 0)}\n"
                        f"- Total documents: {result.get('documents', 0)}\n\n"
                        f"⚠️ **Note:** To make this data searchable, the vector index needs to be updated. "
                        f"Run 'python store_index.py' in the terminal to update the index."
                    )
                    return jsonify({
                        "answer": answer,
                        "sources": [],
                        "ingestion_result": result
                    })
                else:
                    error_msg = result.get("error", "Unknown error occurred")
                    answer = (
                        f"❌ Failed to ingest dataset: {error_msg}\n\n"
                        f"**Please check:**\n"
                        f"- File path is correct\n"
                        f"- File exists in the Data/ directory\n"
                        f"- Format is supported (JSON, CSV, or PDF)\n\n"
                        f"Example: 'ingest dataset medical_conditions.json'"
                    )
                    return jsonify({
                        "answer": answer,
                        "sources": [],
                        "ingestion_result": result
                    })
            else:
                return jsonify({
                    "answer": f"Unknown ingestion action: {ingestion_info.get('action')}",
                    "sources": []
                })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "answer": f"❌ Error with MCP server: {str(e)}",
                "sources": []
            })

    try:
        rag_chain = get_or_create_chain(session_id)
        response = rag_chain({"question": msg})
        
        retrieved_docs = retriever.get_relevant_documents(msg)
        
        sources = []
        seen_sources = set()
        for doc in retrieved_docs:
            source = doc.metadata.get('source', 'unknown')
            source_type = doc.metadata.get('type', 'pdf')
            
            if source != 'unknown':
                filename = os.path.basename(source)
                if filename not in seen_sources:
                    sources.append({
                        "filename": filename,
                        "type": source_type,
                        "path": source
                    })
                    seen_sources.add(filename)
        
        return jsonify({
            "answer": response["answer"],
            "sources": sources
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "answer": f"❌ Error processing your question: {str(e)}",
            "sources": []
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
