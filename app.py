from flask import Flask, render_template,jsonify,request, session
from langchain_openai import OpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from src.helper import download_hugging_face_embeddings
from src.prompt import *
from openai import OpenAI
import os
import uuid

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

docsearch=PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
    namespace="default"
)

retriever= docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})

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

    # Step 1: Check small talk first
    smalltalk_reply = handle_small_talk(msg)
    if smalltalk_reply:
        return jsonify({"answer": smalltalk_reply})

    # Step 2: Use conversational RAG chain
    rag_chain = get_or_create_chain(session_id)
    response = rag_chain({"question": msg})
    return jsonify({"answer": response["answer"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
