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
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=1000)

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
    
    # Custom prompt that explicitly instructs the LLM to use the provided context
    # ConversationalRetrievalChain expects {context} and {question} placeholders
    system_message = """You are a knowledgeable medical assistant. Use the provided context documents to answer medical questions accurately and comprehensively.

CRITICAL INSTRUCTIONS:
1. ALWAYS use the information from the provided context documents to answer MEDICAL questions.
2. If the context contains relevant MEDICAL information, you MUST use it to provide a detailed answer.
3. NEVER say "I don't know" if the context contains relevant medical information - always extract and present what is available.
4. If the context doesn't contain enough information, acknowledge limitations but still provide what you can from the context.
5. Combine information from multiple context documents if available.
6. Be specific and cite which source file the information comes from when possible.
7. IMPORTANT: If the question is clearly NOT medical-related (e.g., asking about geography, locations, cities, countries, recipes, programming, sports, movies, etc.), respond with: "Sorry, I can only answer medical-related questions. Please ask about diseases, symptoms, treatments, medications, health conditions, or other medical topics." Do NOT try to answer non-medical questions even if context is provided.

The context below contains medical information. Use it to answer MEDICAL questions only."""
    
    custom_prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", """Use the following pieces of context to answer the question. The context contains medical information from source documents.

Context:
{context}

Question: {question}

IMPORTANT: First determine if this is a medical question. If it's asking about geography, locations, cities, recipes, programming, or other non-medical topics, respond: "Sorry, I can only answer medical-related questions. Please ask about diseases, symptoms, treatments, medications, health conditions, or other medical topics."

If it IS a medical question, answer based on the context provided above. If the context contains relevant medical information, you MUST use it. Do not say "I don't know" if medical information exists in the context."""),
    ])
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=source_aware_retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": custom_prompt},
        verbose=False
    )
    
    return qa_chain
