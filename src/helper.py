from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, JSONLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import json
import csv
from pathlib import Path
import os


## Extract Data from pdf file
def load_pdf_file(data):
    loader = DirectoryLoader(data,
                             glob="*.pdf",
                             loader_cls=PyPDFLoader) 

    documents=loader.load()
 
    return documents

## Extract Data from JSON file (semi-structured)
def load_json_file(file_path, jq_schema=None):
    """
    Load semi-structured JSON data.
    
    Args:
        file_path: Path to JSON file
        jq_schema: Optional jq schema for extracting specific fields
                   Example: ".[] | {question: .question, answer: .answer}"
    """
    if jq_schema:
        loader = JSONLoader(file_path=file_path, jq_schema=jq_schema)
        documents = loader.load()
    else:
        # Fallback: load entire JSON and convert to text
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        documents = []
        if isinstance(data, list):
            for idx, item in enumerate(data):
                text = json.dumps(item, indent=2)
                metadata = {
                    "source": file_path,
                    "type": "json",
                    "index": idx
                }
                documents.append(Document(page_content=text, metadata=metadata))
        else:
            text = json.dumps(data, indent=2)
            metadata = {"source": file_path, "type": "json"}
            documents.append(Document(page_content=text, metadata=metadata))
    
    return documents

## Extract Data from CSV file (semi-structured)
def load_csv_file(file_path, source_column=None):
    """
    Load semi-structured CSV data.
    
    Args:
        file_path: Path to CSV file
        source_column: Optional column name to use as source text
    """
    loader = CSVLoader(file_path=file_path, source_column=source_column)
    documents = loader.load()
    
    # Add metadata to identify CSV source
    for doc in documents:
        if 'source' not in doc.metadata:
            doc.metadata['source'] = file_path
        doc.metadata['type'] = 'csv'
    
    return documents

## Load all supported file types from directory
def load_mixed_data(data_dir):
    """
    Load documents from directory supporting multiple formats:
    - PDF files
    - JSON files
    - CSV files
    """
    data_path = Path(data_dir)
    all_documents = []
    
    # Load PDFs
    pdf_files = list(data_path.glob("*.pdf"))
    if pdf_files:
        pdf_docs = load_pdf_file(data_dir)
        all_documents.extend(pdf_docs)
    
    # Load JSONs
    json_files = list(data_path.glob("*.json"))
    for json_file in json_files:
        try:
            json_docs = load_json_file(str(json_file))
            all_documents.extend(json_docs)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    # Load CSVs
    csv_files = list(data_path.glob("*.csv"))
    for csv_file in csv_files:
        try:
            csv_docs = load_csv_file(str(csv_file))
            all_documents.extend(csv_docs)
        except Exception as e:
            print(f"Error loading {csv_file}: {e}")
    
    return all_documents
 
## Split data into Text Chunks
def text_split(all_extract_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks=text_splitter.split_documents(all_extract_data)
    
    # Ensure all chunks have source metadata
    for chunk in text_chunks:
        if 'source' not in chunk.metadata:
            chunk.metadata['source'] = 'unknown'
        if 'type' not in chunk.metadata:
            chunk.metadata['type'] = 'text'
    
    return text_chunks

## download hugging face embeddings
def download_hugging_face_embeddings(model_name='sentence-transformers/all-MiniLM-L6-v2'):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings