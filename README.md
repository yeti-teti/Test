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


## Project Structure
MedicalChatbot/
│── public/ # Static files (HTML, CSS, JS)
│── src/ # Source code
│ ├── helper.py # Embedding download function
│ ├── prompt.py # RAG chain + prompt
│── app.py # Flask entrypoint
│── requirements.txt # Python dependencies
│── README.md # Documentation
│── .env # Environment variables

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

### 5. Run the app
python app.py

Now open http://127.0.0.1:5000/ in your browser.

### Usage
Ask a medical-related question → bot retrieves from Pinecone DB.

Non-medical questions → bot responds with:
"Sorry, I can only answer medical-related questions."


### Future Work
Implement Agentic RAG (ReAct agent + external APIs)
Add RAGAS evaluation metrics



