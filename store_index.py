from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
import os


load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
if not PINECONE_API_KEY:
    raise ValueError('PINECONE_API_KEY is not set. Please configure it in your environment or .env file.')

os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY

# Load source documents and compute embeddings
extracted_data = load_pdf_file(data='Data/')
text_chunks = text_split(extracted_data)
embeddings = download_hugging_face_embeddings()

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'medicalbot'

# Create the index only if it does not already exist
existing_indexes = {index.name for index in pc.list_indexes().indexes}
if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=384,  # MiniLM-L6-v2 → 384 dims
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1'),
    )

# Embed each chunk and upsert the embeddings into the Pinecone index
PineconeVectorStore.from_documents(
    text_chunks,
    embeddings,
    index_name=index_name,
    namespace='default',
)
