# src/prompt.py
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate


def build_rag_chain(retriever):
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
