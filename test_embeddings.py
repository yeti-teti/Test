"""
Script to test different embedding models for the Medical Chatbot.
Compares retrieval performance between models using test queries.
"""
import os
import re
import time
from dotenv import load_dotenv
from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Models to test
MODELS = [
    'sentence-transformers/all-MiniLM-L6-v2',  # Current model
    'sentence-transformers/all-MiniLM-L12-v2',  # Similar but larger
    'sentence-transformers/all-mpnet-base-v2',  # Better performance, 768 dims
]

# Test queries (medical-related)
TEST_QUERIES = [
    "What are the symptoms of diabetes?",
    "How is hypertension treated?",
    "What causes heart disease?",
    "Explain the effects of aspirin on blood clots.",
    "What is the treatment for pneumonia?",
]

def create_test_index(model_name, dimension):
    """Create a test index for the model."""
    pc = Pinecone(api_key=PINECONE_API_KEY)

    suffix = re.sub(r'[^a-z0-9-]', '', model_name.split('/')[-1].lower())
    index_name = f"medicalbot-test-{suffix}"

    # Delete if exists
    if index_name in [idx.name for idx in pc.list_indexes().indexes]:
        pc.delete_index(index_name)

    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

    # Wait for the serverless index to be ready before upserting documents
    while True:
        status = pc.describe_index(index_name).status
        if status.get("ready"):
            break
        time.sleep(2)

    return index_name

def evaluate_model(model_name):
    """Evaluate a single model."""
    print(f"\nEvaluating model: {model_name}")

    # Get dimension (hardcoded for known models)
    dims = {
        'sentence-transformers/all-MiniLM-L6-v2': 384,
        'sentence-transformers/all-MiniLM-L12-v2': 384,
        'sentence-transformers/all-mpnet-base-v2': 768,
    }
    dim = dims.get(model_name, 384)

    # Create index
    index_name = create_test_index(model_name, dim)

    # Load data and create embeddings
    extracted_data = load_pdf_file(data='Data/')
    text_chunks = text_split(extracted_data)
    embeddings = download_hugging_face_embeddings(model_name)

    # Create vector store
    docsearch = PineconeVectorStore.from_documents(
        documents=text_chunks,
        embedding=embeddings,
        index_name=index_name,
        namespace="test"
    )

    # Test retrieval
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    results = {}
    for query in TEST_QUERIES:
        docs = retriever.get_relevant_documents(query)
        results[query] = [doc.page_content[:200] + "..." for doc in docs]  # First 200 chars
        print(f"Retrieved {len(docs)} docs for '{query}' using {model_name}")

    # Clean up (optional, comment out if you want to keep for inspection)
    pc = Pinecone(api_key=PINECONE_API_KEY)
    # pc.delete_index(index_name)

    return results

def main():
    """Main evaluation function."""
    all_results = {}

    for model in MODELS:
        try:
            results = evaluate_model(model)
            all_results[model] = results
        except Exception as e:
            print(f"Error evaluating {model}: {e}")
            all_results[model] = str(e)

    # Print comparison
    print("\n" + "="*80)
    print("EMBEDDING MODEL COMPARISON RESULTS")
    print("="*80)

    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print("-" * 50)
        for model, results in all_results.items():
            if isinstance(results, dict) and query in results:
                print(f"{model}:")
                for i, doc in enumerate(results[query][:2], 1):  # Show top 2
                    print(f"  {i}. {doc}")
                print()
            else:
                print(f"{model}: Error - {results}")

    print("\nFor quantitative metrics (precision, recall, etc.), run RAGAS evaluation with QA pairs.")

if __name__ == "__main__":
    main()