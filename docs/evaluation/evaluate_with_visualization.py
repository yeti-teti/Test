"""
RAGAS Evaluation Script with Visualization

This script evaluates the RAG system using the RAGAS framework and generates
comprehensive visualizations comparing pre- and post-dataset integration results.

It computes metrics like faithfulness, answer relevance, context precision, and context recall.

Usage: python docs/evaluation/evaluate_with_visualization.py
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

# Add project root to path
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
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore

# Try to import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib not available. Skipping visualizations.")
    print("   Install with: pip install matplotlib")

load_dotenv()
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load QA dataset - try expanded version first, fallback to original
qa_dataset_path = Path(__file__).parent / 'qa_dataset_expanded.json'
if not qa_dataset_path.exists():
    qa_dataset_path = Path(__file__).parent / 'qa_dataset.json'

with open(qa_dataset_path, 'r') as f:
    qa_data = json.load(f)


def build_rag_chain_for_eval(retriever):
    """Build RAG chain for evaluation (modified to return contexts)."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4, max_tokens=500)

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

# Set limit
def prepare_evaluation_data(limit: int = 50):
    """Run RAG on QA pairs and prepare data for RAGAS."""
    # Setup retriever
    embeddings = download_hugging_face_embeddings()
    index_name = "medicalbot"
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings,
        namespace="default"
    )
    retriever = docsearch.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 20, "lambda_mult": 0.5}
    )

    rag_chain = build_rag_chain_for_eval(retriever)

    eval_data = []
    qa_items = qa_data[:limit] if limit else qa_data
    
    for idx, item in enumerate(qa_items):
        question = item['question']
        ground_truth = item['ground_truth']

        # Retrieve contexts explicitly and run the chain for the answer
        retrieved_docs = retriever.invoke(question)
        response = rag_chain.invoke({"input": question})

        # Extract answer and contexts (use retriever output to ensure alignment)
        answer = response['answer']
        contexts = [doc.page_content for doc in retrieved_docs]

        eval_data.append({
            'question': question,
            'answer': answer,
            'contexts': contexts,
            'reference': ground_truth
        })
        
        # Progress indicator
        if (idx + 1) % 5 == 0:
            print(f"  Processed {idx + 1}/{len(qa_items)} questions...")

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


def create_comparison_visualization(results_df: pd.DataFrame, dataset_name: str = "Current"):
    """Create visualization of evaluation metrics."""
    
    if not MATPLOTLIB_AVAILABLE:
        print("⚠️  Visualization skipped (matplotlib not available)")
        return None
    
    metrics = ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Medical Chatbot RAGAS Evaluation Metrics - {dataset_name}', 
                 fontsize=16, fontweight='bold')
    
    axes = axes.flatten()
    
    for idx, metric in enumerate(metrics):
        if metric in results_df.columns:
            values = results_df[metric]
            
            # Create histogram
            axes[idx].hist(values, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
            axes[idx].axvline(values.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {values.mean():.3f}')
            axes[idx].set_title(f'{metric.replace("_", " ").title()}', fontweight='bold')
            axes[idx].set_xlabel('Score')
            axes[idx].set_ylabel('Frequency')
            axes[idx].set_xlim([0, 1])
            axes[idx].legend()
            axes[idx].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def create_comparison_bar_chart(pre_results: Dict[str, float], 
                                post_results: Dict[str, float]):
    """Create bar chart comparing pre and post metrics."""
    
    if not MATPLOTLIB_AVAILABLE:
        return None
    
    metrics = list(pre_results.keys())
    pre_values = [pre_results[m] for m in metrics]
    post_values = [post_results[m] for m in metrics]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars1 = ax.bar(x - width/2, pre_values, width, label='Pre-Integration', 
                   color='lightcoral', edgecolor='black', alpha=0.8)
    bars2 = ax.bar(x + width/2, post_values, width, label='Post-Integration (MIMIC-IV)', 
                   color='lightgreen', edgecolor='black', alpha=0.8)
    
    ax.set_xlabel('Metrics', fontweight='bold')
    ax.set_ylabel('Score', fontweight='bold')
    ax.set_title('Medical Chatbot Performance: Pre vs Post MIMIC-IV Dataset Integration', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics])
    ax.set_ylim([0, 1])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    return fig


def load_previous_results() -> Dict[str, float]:
    """Load previous evaluation results if they exist."""
    results_csv = Path(__file__).parent / 'ragas_results.csv'
    
    if results_csv.exists():
        df = pd.read_csv(results_csv)
        metrics = ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']
        return {
            metric: df[metric].mean() if metric in df.columns else 0.0
            for metric in metrics
        }
    
    return None


def save_results_summary(results_df: pd.DataFrame, pre_results: Dict[str, float] = None):
    """Save evaluation results summary."""
    output_dir = Path(__file__).parent
    
    # Detailed CSV results
    results_df.to_csv(output_dir / 'ragas_results_detailed.csv', index=False)
    
    # Summary statistics
    summary = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'total_qa_pairs': len(results_df),
        'metrics': {}
    }
    
    for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
        if metric in results_df.columns:
            summary['metrics'][metric] = {
                'mean': float(results_df[metric].mean()),
                'std': float(results_df[metric].std()),
                'min': float(results_df[metric].min()),
                'max': float(results_df[metric].max())
            }
    
    # Add comparison if pre-results available
    if pre_results:
        summary['pre_integration'] = pre_results
        summary['improvements'] = {}
        for metric in pre_results.keys():
            improvement = summary['metrics'][metric]['mean'] - pre_results[metric]
            summary['improvements'][metric] = float(improvement)
    
    with open(output_dir / 'ragas_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    return summary


def main():
    """Main evaluation function."""
    print("\n" + "="*60)
    print("Medical Chatbot RAGAS Evaluation with Visualization")
    print("="*60 + "\n")
    
    # Check for previous results
    print("📊 Checking for previous evaluation results...")
    pre_results = load_previous_results()
    
    if pre_results:
        print(f"✅ Found previous results (pre-integration)")
        print(f"   - Faithfulness: {pre_results['faithfulness']:.3f}")
        print(f"   - Answer Relevancy: {pre_results['answer_relevancy']:.3f}")
        print(f"   - Context Precision: {pre_results['context_precision']:.3f}")
        print(f"   - Context Recall: {pre_results['context_recall']:.3f}")
    else:
        print("ℹ️  No previous results found (first evaluation)")
        pre_results = None
    
    # Run evaluation
    print("\n🔄 Preparing evaluation data...")
    eval_data = prepare_evaluation_data()
    print(f"✅ Prepared {len(eval_data)} QA pairs for evaluation")
    
    print("\n⏳ Running RAGAS evaluation (this may take several minutes)...")
    results = run_ragas_evaluation(eval_data)
    results_df = results.to_pandas()
    
    print("\n" + "="*60)
    print("RAGAS Evaluation Results (Post-Integration)")
    print("="*60)
    print(results)
    
    # Calculate post-results
    post_results = {}
    for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
        if metric in results_df.columns:
            post_results[metric] = float(results_df[metric].mean())
    
    # Print summary statistics
    print("\n📈 Summary Statistics:")
    print("-" * 60)
    for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
        if metric in results_df.columns:
            mean_score = results_df[metric].mean()
            std_score = results_df[metric].std()
            print(f"{metric.replace('_', ' ').title():.<30} {mean_score:.3f} ± {std_score:.3f}")
    
    # Compare with pre-results if available
    if pre_results:
        print("\n📊 Pre vs Post Integration Comparison:")
        print("-" * 60)
        for metric in pre_results.keys():
            pre_val = pre_results[metric]
            post_val = post_results[metric]
            improvement = post_val - pre_val
            improvement_pct = (improvement / pre_val * 100) if pre_val > 0 else 0
            arrow = "↑" if improvement > 0 else "↓" if improvement < 0 else "→"
            print(f"{metric.replace('_', ' ').title():.<30} {pre_val:.3f} → {post_val:.3f} {arrow} ({improvement_pct:+.1f}%)")
    
    # Save results
    print("\n💾 Saving results...")
    summary = save_results_summary(results_df, pre_results)
    print(f"✅ Saved detailed results to ragas_results_detailed.csv")
    print(f"✅ Saved summary to ragas_summary.json")
    
    # Create visualizations
    if MATPLOTLIB_AVAILABLE:
        print("\n📊 Creating visualizations...")
        
        # Individual metrics distribution
        fig1 = create_comparison_visualization(results_df, "Post-Integration")
        if fig1:
            fig1.savefig(Path(__file__).parent / 'metrics_distribution_post.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved metrics distribution plot to metrics_distribution_post.png")
        
        # Pre vs Post comparison
        if pre_results:
            fig2 = create_comparison_bar_chart(pre_results, post_results)
            if fig2:
                fig2.savefig(Path(__file__).parent / 'pre_vs_post_comparison.png', dpi=300, bbox_inches='tight')
                print(f"✅ Saved pre/post comparison plot to pre_vs_post_comparison.png")
        
        plt.close('all')
    
    print("\n" + "="*60)
    print("✅ Evaluation Complete!")
    print("="*60)
    print(f"\n📁 Output files in docs/evaluation/:")
    print(f"   - ragas_results_detailed.csv (all QA pair scores)")
    print(f"   - ragas_summary.json (aggregate statistics)")
    if MATPLOTLIB_AVAILABLE:
        print(f"   - metrics_distribution_post.png (metric distributions)")
        if pre_results:
            print(f"   - pre_vs_post_comparison.png (improvement visualization)")
    print()


if __name__ == "__main__":
    main()

