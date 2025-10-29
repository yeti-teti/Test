# src/prompt.py
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from typing import List
import os


def build_rag_chain(retriever):
    """Build RAG chain without memory (for single-turn queries)."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=500)

    system_prompt = """You are a MEDICAL chatbot.
    Use ONLY the provided medical context to answer.
    ALWAYS cite your sources at the end of your response.
    Extract the actual source filename from the context metadata and cite it.
    Format sources as: [Source: actual_filename.pdf] or [Source: actual_filename.json]
    Use the exact filename from the source metadata, not a placeholder.
    If the user asks something unrelated to health or medicine, reply:
    'Sorry, I can only answer medical-related questions.'"""

    # Must include {context} so retriever can inject docs
    prompt = ChatPromptTemplate.from_template(
        """
        {system_prompt}

        Context:
        {context}

        Question:
        {input}

        Answer (include source citations at the end using the exact filenames from the context):
        """
    ).partial(system_prompt=system_prompt)

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain


def build_conversational_rag_chain(retriever):
    """Build conversational RAG chain with memory for multi-turn interactions."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=500)

    memory = ConversationBufferWindowMemory(
        k=5,  # Keep last 5 interactions
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    class SourceAwareRetriever(BaseRetriever):
        """Wrapper retriever that formats documents with source filenames."""
        base_retriever: BaseRetriever
        
        def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
        ) -> List[Document]:
            """Get documents and format them with source filenames."""
            docs = self.base_retriever.get_relevant_documents(query)
            formatted_docs = []
            for doc in docs:
                source = doc.metadata.get('source', 'unknown')
                filename = os.path.basename(source) if source != 'unknown' else 'unknown'
                new_content = f"[Source File: {filename}]\n{doc.page_content}"
                formatted_doc = Document(
                    page_content=new_content,
                    metadata=doc.metadata
                )
                formatted_docs.append(formatted_doc)
            return formatted_docs
    
    source_aware_retriever = SourceAwareRetriever(base_retriever=retriever)
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=source_aware_retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )
    
    return qa_chain
