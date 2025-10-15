from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings


## Extract Data from pdf file
def load_pdf_file(data):
    loader = DirectoryLoader(data,
                             glob="*.pdf",
                             loader_cls=PyPDFLoader) 

    documents=loader.load()
 
    return documents
 
## Split data into Text Chunks
def text_split(all_extract_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks=text_splitter.split_documents(all_extract_data)
    return text_chunks

## download hugging face embeddings
def download_hugging_face_embeddings(model_name='sentence-transformers/all-MiniLM-L6-v2'):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return embeddings