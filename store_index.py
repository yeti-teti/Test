from src.helper import load_pdf_file,text_split,download_hugging_face_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
import os


load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

## embedding model
extracted_data=load_pdf_file(data='data/')
text_chunks=text_split(extracted_data)
embeddings=download_hugging_face_embeddings()

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medicalbot"

pc.create_index(
        name=index_name,
        dimension=384,        # MiniLM-L6-v2 → 384 dims
        metric="cosine",      # cosine is best for semantic embeddings
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

#Embeded each chunk and upsert the embeddings into Pinecone index
docsearch=PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
    namespace="default"
)
