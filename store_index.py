from src.helper import load_pdf_file, load_mixed_data, text_split, download_hugging_face_embeddings
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

# Load source documents from multiple formats (PDF, JSON, CSV)
print("Loading documents from Data/ directory...")
extracted_data = load_mixed_data(data_dir='Data/')
print(f"Loaded {len(extracted_data)} documents")

# Split into chunks
print("Splitting documents into chunks...")
text_chunks = text_split(extracted_data)
print(f"Created {len(text_chunks)} text chunks")

# Download embeddings
print("Downloading embeddings model...")
embeddings = download_hugging_face_embeddings()

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = 'medicalbot'

# Create the index only if it does not already exist
existing_indexes = {index.name for index in pc.list_indexes().indexes}
if index_name not in existing_indexes:
    print(f"Creating Pinecone index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=384,  # MiniLM-L6-v2 → 384 dims
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1'),
    )
else:
    print(f"Index {index_name} already exists")

# Embed each chunk and upsert the embeddings into the Pinecone index
print("Uploading embeddings to Pinecone...")
PineconeVectorStore.from_documents(
    text_chunks,
    embeddings,
    index_name=index_name,
    namespace='default',
)
print("Indexing complete!")
