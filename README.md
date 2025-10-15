# MedicalChatbot

## Requirements
- Python 3.11 (tested on 3.11.9)
- pip >= 22


# Medical Chatbot (RAG + Flask)

A Retrieval-Augmented Generation (RAG) medical chatbot built with:
- **Flask** for the web interface
- **LangChain** for orchestration
- **Pinecone** as vector database
- **OpenAI GPT model** for language generation
- **Hugging Face embeddings** for document representation


## Features
- Responsive chat UI (works on laptop & mobile)
- Retrieval-based answers (no hallucinations)
- Restricts responses to **medical-related queries only**
- Customizable system prompt


## Architecture Overview

The Medical Chatbot follows a RAG (Retrieval-Augmented Generation) architecture:

1. **Data Ingestion**: Medical PDFs are loaded, split into chunks, and embedded using Hugging Face models.
2. **Vector Storage**: Embeddings are stored in Pinecone for efficient similarity search.
3. **Query Processing**: User queries are embedded and used to retrieve relevant document chunks.
4. **Answer Generation**: Retrieved context is fed to OpenAI GPT model with a medical-specific prompt.
5. **Response Filtering**: Non-medical queries are handled with predefined responses.

### Key Components and Relationships

- **Flask App (`app.py`)**: Main web server handling HTTP requests and responses.
  - Routes: `/` for index page, `/ask` for chat queries.
  - Integrates small talk handler and RAG chain.

- **Small Talk Handler**: Processes greetings, thanks, and farewells without invoking RAG.
  - Relationship: Prioritizes over RAG chain for efficiency.

- **RAG Chain (`src/prompt.py`)**: Core logic combining retrieval and generation.
  - Uses LangChain's `create_retrieval_chain` and `create_stuff_documents_chain`.
  - Relationship: Receives retriever from Pinecone, sends prompts to OpenAI.

- **Retriever**: Queries Pinecone vector store for top-k similar chunks.
  - Relationship: Depends on embeddings from Hugging Face.

- **Vector Store (Pinecone)**: Stores embedded document chunks.
  - Relationship: Indexed via `store_index.py` with embeddings.

- **Embedding Model (`src/helper.py`)**: Downloads and uses Hugging Face `sentence-transformers/all-MiniLM-L6-v2`.
  - Relationship: Used for both indexing documents and querying.

- **LLM (OpenAI GPT-4o-mini)**: Generates answers based on context.
  - Relationship: Receives structured prompts with medical context.

### Data Flow
1. User submits query via web UI.
2. Flask checks for small talk; if yes, responds directly.
3. Query embedded using Hugging Face model.
4. Embedding used to search Pinecone for relevant chunks.
5. Retrieved chunks combined into prompt with system instructions.
6. Prompt sent to OpenAI for generation.
7. Generated answer returned to user.

## Project Structure
```
MedicalChatbot/
│── Data/                          # Medical PDF documents
│── docs/                          # Documentation
│   ├── C4_Diagrams.md            # C4 model diagrams
│   └── diagrams/                 # Architecture diagrams
│── src/                          # Source code
│   ├── helper.py                 # Embedding and data loading functions
│   ├── prompt.py                 # RAG chain and prompt templates
│── static/                       # Static web assets
│   ├── style.css                 # CSS styles
│── templates/                    # HTML templates
│   ├── index.html                # Main chat interface
│── app.py                        # Flask application entrypoint
│── store_index.py                # Script to create Pinecone index
│── requirements.txt              # Python dependencies
│── setup.py                      # Package setup
│── README.md                     # This file
│── LICENSE                       # License information
```

## Setup Instructions

### 1. Clone the repository
Project repo: https://github.com/namitaChhantyal/MedicalChatbot.git

```bash
git clone https://github.com/yourusername/MedicalChatbot.git
cd MedicalChatbot

### 2. Create & activate virtual environment
Create Virtual environment
py -3.11 -m venv medibot
# Windows
medibot\Scripts\activate
# Mac/Linux
source medibot/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Setup environment variables
Create a .env file in root folder
OPENAI_API_KEY=your_openai_api_key
OPENAI_PROJECT_KEY=your_project_key
PINECONE_API_KEY=your_pinecone_api_key

### 5. Index the data (one-time setup)
python store_index.py

### 6. Run the app
python app.py

Now open http://127.0.0.1:5000/ in your browser.

## Usage
Ask a medical-related question → bot retrieves from Pinecone DB.

Non-medical questions → bot responds with:
"Sorry, I can only answer medical-related questions."

## Evaluation
The chatbot can be evaluated using RAGAS framework with custom QA pairs.
See `docs/evaluation/` for evaluation scripts and results.

## Future Work
- Implement Agentic RAG (ReAct agent + external APIs)
- Add conversation memory for multi-turn interactions
- Integrate additional data sources
- Enhance evaluation metrics