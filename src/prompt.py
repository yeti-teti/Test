# src/prompt.py
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.prompts import ChatPromptTemplate


def build_rag_chain(retriever):
    """Build RAG chain without memory (for single-turn queries)."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=500)

    system_prompt = """You are a MEDICAL chatbot.
    Use ONLY the provided medical context to answer.
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

        Answer:
        """
    ).partial(system_prompt=system_prompt)

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain


def build_conversational_rag_chain(retriever):
    """Build conversational RAG chain with memory for multi-turn interactions."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=500)

    system_prompt = """You are a MEDICAL chatbot.
    Use ONLY the provided medical context to answer.
    Maintain conversation coherence by considering previous interactions.
    If the user asks something unrelated to health or medicine, reply:
    'Sorry, I can only answer medical-related questions.'"""

    memory = ConversationBufferWindowMemory(
        k=5,  # Keep last 5 interactions
        memory_key="chat_history",
        return_messages=True
    )

    # Use ConversationalRetrievalChain for memory support
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": ChatPromptTemplate.from_template(
            f"{system_prompt}\n\nContext:\n{{context}}\n\nChat History:\n{{chat_history}}\n\nQuestion: {{question}}\n\nAnswer:"
        )}
    )

    return qa_chain
