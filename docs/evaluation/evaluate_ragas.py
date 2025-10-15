"""
RAGAS Evaluation Script for Medical Chatbot

This script evaluates the RAG system using the RAGAS framework.
It computes metrics like faithfulness, answer relevance, context precision, and context recall.

Usage: python docs/evaluation/evaluate_ragas.py
"""

import os
import json

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset
from langchain_openai import OpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore


load_dotenv()
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Load QA dataset
with open('docs/evaluation/qa_dataset.json', 'r') as f:
    qa_data = json.load(f)

def build_rag_chain_for_eval(retriever):
    """Build RAG chain for evaluation (modified to return contexts)."""
    llm = OpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=500)

    system_prompt = """You are a MEDICAL chatbot.
    Use ONLY the provided medical context to answer.
    If the user asks something unrelated to health or medicine, reply:
    'Sorry, I can only answer medical-related questions.'"""

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

def prepare_evaluation_data():
    """Run RAG on QA pairs and prepare data for RAGAS."""
    # Setup retriever
    embeddings = download_hugging_face_embeddings()
    index_name = "medicalbot"
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings,
        namespace="default"
    )
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    rag_chain = build_rag_chain_for_eval(retriever)

    eval_data = []
    for item in qa_data:
        question = item['question']
        ground_truth = item['ground_truth']

        # Get RAG response
        response = rag_chain.invoke({"input": question})

        # Extract answer and contexts
        answer = response['answer']
        contexts = [doc.page_content for doc in response['context']]

        eval_data.append({
            'question': question,
            'answer': answer,
            'contexts': contexts,
            'ground_truth': ground_truth
        })

    return eval_data

def run_ragas_evaluation(eval_data):
    """Run RAGAS evaluation on the prepared data."""
    # Create Dataset
    dataset = Dataset.from_list(eval_data)

    # Define metrics
    metrics = [
        faithfulness,      # Measures how well the answer is supported by the context
        answer_relevancy,  # Measures how relevant the answer is to the question
        context_precision, # Measures if the retrieved contexts are relevant to the question
        context_recall,    # Measures if the retrieved contexts cover the ground truth answer
    ]

    # Evaluate
    results = evaluate(dataset, metrics=metrics)

    return results

def main():
    """Main evaluation function."""
    print("Preparing evaluation data...")
    eval_data = prepare_evaluation_data()

    print(f"Evaluating {len(eval_data)} QA pairs...")
    results = run_ragas_evaluation(eval_data)

    print("\nRAGAS Evaluation Results:")
    print("=" * 50)
    print(results)

    # Save results
    results_df = results.to_pandas()
    results_df.to_csv('docs/evaluation/ragas_results.csv', index=False)

    # Print summary statistics
    print("\nSummary Statistics:")
    print("-" * 30)
    for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
        if metric in results_df.columns:
            mean_score = results_df[metric].mean()
            print(f"{metric}: {mean_score:.3f}")

    print("\nDetailed results saved to docs/evaluation/ragas_results.csv")

if __name__ == "__main__":
    main()