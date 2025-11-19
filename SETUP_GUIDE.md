# 🚀 Complete Setup Guide - Medical Chatbot

This guide provides detailed step-by-step instructions to set up and run the Medical Chatbot from scratch.

---

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.11 or higher** installed
   - Check version: `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Git** installed
   - Check version: `git --version`
   - Download from: https://git-scm.com/downloads

3. **API Keys** (you'll need these):
   - OpenAI API Key: https://platform.openai.com/api-keys
   - Pinecone API Key: https://www.pinecone.io/ (free tier available)
   - Exa AI API Key: https://exa.ai/ (for web search)

---

## 🔧 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/namitaChhantyal/MedicalChatbot.git

# Navigate into the project directory
cd MedicalChatbot
```

---

### Step 2: Create Virtual Environment

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv medibot

# Activate virtual environment
source medibot/bin/activate
```

**On Windows:**
```bash
# Create virtual environment
python -m venv medibot

# Activate virtual environment
medibot\Scripts\activate
```

**Verify activation:**
You should see `(medibot)` at the beginning of your terminal prompt.

---

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**This will install:**
- Flask (web server)
- LangChain (RAG framework)
- Pinecone (vector database)
- OpenAI (LLM)
- Exa (web search)
- HuggingFace transformers (embeddings)
- And other dependencies

---

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# Create .env file
touch .env
```

**Edit `.env` and add your API keys:**

```env
# OpenAI Configuration
OPENAI_API_KEY="your-openai-api-key-here"
OPENAI_PROJECT="your-openai-project-id-here"

# Pinecone Configuration
PINECONE_API_KEY="your-pinecone-api-key-here"

# Exa AI Configuration (for web search)
EXA_API_KEY="your-exa-api-key-here"

# Flask Configuration
SECRET_KEY="your-secret-key-for-sessions"
```

**How to get API keys:**

1. **OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key and paste it in `.env`

2. **Pinecone API Key:**
   - Sign up at https://www.pinecone.io/
   - Go to "API Keys" in your dashboard
   - Copy the key and paste it in `.env`

3. **Exa AI API Key:**
   - Sign up at https://exa.ai/
   - Get your API key from the dashboard
   - Copy and paste it in `.env`

---

### Step 5: Prepare Your Data

The chatbot needs medical documents to answer questions.

**Option A: Use Existing Data**
```bash
# The repository should already have some medical PDFs in the Data/ folder
ls Data/
```

**Option B: Add Your Own Medical Documents**
```bash
# Add PDF, JSON, or CSV files to the Data/ directory
cp /path/to/your/medical_document.pdf Data/
```

**Supported formats:**
- `.pdf` - Medical textbooks, research papers
- `.json` - Structured medical data
- `.csv` - Tabular medical data

---

### Step 6: Create the Vector Index

This step processes your documents and stores them in Pinecone for fast retrieval.

```bash
# Run the indexing script
python3 store_index.py
```

**What this does:**
1. Reads all files from `Data/` directory
2. Splits documents into chunks
3. Creates embeddings using HuggingFace model
4. Uploads embeddings to Pinecone

**Expected output:**
```
Loading documents...
Splitting documents into chunks...
Creating embeddings...
Uploading to Pinecone...
✅ Successfully indexed X documents
```

**⏱️ Time:** This may take 5-15 minutes depending on the number of documents.

---

### Step 7: (Optional) Ingest Additional Datasets

You can add more datasets using the MCP (Model Context Protocol) system:

```bash
# Ingest a JSON dataset
python3 ingest_dataset.py Data/medical_conditions.json json

# Ingest a CSV dataset
python3 ingest_dataset.py Data/diseases.csv csv

# List all ingested datasets
python3 ingest_dataset.py --list
```

**After adding new datasets, re-run the indexing:**
```bash
python3 store_index.py
```

---

### Step 8: Start the Application

```bash
# Start the Flask server
python3 app.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:8080
 * Debug mode: on
 * Debugger is active!
```

**The server is now running!** 🎉

---

### Step 9: Access the Chatbot

Open your web browser and go to:

```
http://localhost:8080
```

**You should see:**
- A chat interface with "Medical Chatbot" header
- An input box to ask questions
- A "Send" button

---

## 💬 Using the Chatbot

### Ask Medical Questions

**Example questions:**
```
What are the symptoms of diabetes?
How is hypertension treated?
What causes cancer?
use exa ai to find me most common diseases
```

### What You'll See

1. **Your question** appears on the right (blue bubble)
2. **Bot's answer** appears on the left (white bubble)
3. **Source breakdown** shows where the information came from:
   - 📚 **RAG Sources**: From your indexed documents
   - 📊 **MCP**: From ingested datasets
   - 🌐 **Web Search (Exa AI)**: From live web search

### Non-Medical Questions

If you ask non-medical questions:
```
Where is New York?
What's the weather today?
```

The bot will respond:
```
Sorry, I can only answer medical-related questions.
```

---

## 🔍 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
source medibot/bin/activate  # Mac/Linux
medibot\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue: "API key not found" errors

**Solution:**
```bash
# Check if .env file exists
cat .env

# Make sure all API keys are set correctly
# No spaces around the = sign
# Keys should be in quotes
```

---

### Issue: "Port 8080 already in use"

**Solution:**
```bash
# Kill the process using port 8080
lsof -ti:8080 | xargs kill -9

# Or change the port in app.py (last line):
# app.run(host="0.0.0.0", port=8081, debug=True)
```

---

### Issue: Exa AI not working

**Check the terminal output for:**
```
🔍 Exa: Searching for '...' with 5 results
✅ Exa: Found 5 results
```

**If you see errors:**
1. Verify `EXA_API_KEY` is set in `.env`
2. Check your Exa AI account has credits
3. Look at terminal for specific error messages

---

### Issue: No answers from RAG sources

**Solution:**
```bash
# Re-run the indexing
python3 store_index.py

# Check Pinecone dashboard to verify index exists
# Go to https://app.pinecone.io/
```

---

## 📊 Testing the System

### Test 1: Basic Medical Question
```
Question: What are the symptoms of anemia?

Expected: Bot provides symptoms with source citations
```

### Test 2: Web Search
```
Question: use exa ai to find top causes of cancer

Expected: Bot shows web sources (🌐 Web: 3-5) and provides comprehensive answer
```

### Test 3: Non-Medical Question
```
Question: Where is Paris?

Expected: "Sorry, I can only answer medical-related questions."
```

### Test 4: Check Sources
```
After any answer, look for:
- Source breakdown box
- RAG/MCP/Web counts
- Clickable links to web sources
```

---

## 🛑 Stopping the Application

**To stop the server:**
1. Go to the terminal where the server is running
2. Press `Ctrl + C`

**To deactivate virtual environment:**
```bash
deactivate
```

---

## 🔄 Restarting the Application

**Every time you want to use the chatbot:**

```bash
# 1. Navigate to project directory
cd /path/to/MedicalChatbot

# 2. Activate virtual environment
source medibot/bin/activate  # Mac/Linux
medibot\Scripts\activate     # Windows

# 3. Start the server
python3 app.py

# 4. Open browser to http://localhost:8080
```

---

## 📁 Project Structure

```
MedicalChatbot/
├── Data/                    # Your medical documents (PDF, JSON, CSV)
├── src/                     # Source code
│   ├── helper.py           # Embedding functions
│   ├── prompt.py           # RAG chain logic
│   ├── exa_web_search.py   # Exa AI integration
│   └── mcp_client.py       # MCP dataset management
├── static/                  # CSS styles
│   └── style.css
├── templates/               # HTML templates
│   └── index.html
├── app.py                   # Main Flask application
├── store_index.py          # Indexing script
├── ingest_dataset.py       # Dataset ingestion
├── requirements.txt        # Python dependencies
├── .env                    # API keys (create this)
└── README.md              # Documentation
```

---

## 🎯 Quick Start Summary

```bash
# 1. Clone and navigate
git clone https://github.com/namitaChhantyal/MedicalChatbot.git
cd MedicalChatbot

# 2. Create virtual environment
python3 -m venv medibot
source medibot/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with API keys
touch .env
# Edit .env and add your API keys

# 5. Index your documents
python3 store_index.py

# 6. Start the app
python3 app.py

# 7. Open browser
# Go to http://localhost:8080
```

---

## 📞 Support

If you encounter issues:

1. **Check the terminal output** for error messages
2. **Verify all API keys** are set correctly in `.env`
3. **Ensure virtual environment** is activated
4. **Check Pinecone dashboard** to verify index exists
5. **Review the logs** in the terminal for debugging info

---

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] `.env` file created with all API keys
- [ ] Documents added to `Data/` folder
- [ ] `store_index.py` completed successfully
- [ ] `python3 app.py` running without errors
- [ ] Browser shows chat interface at `http://localhost:8080`
- [ ] Bot responds to medical questions
- [ ] Source breakdown shows RAG/MCP/Web sources
- [ ] Exa AI web search working (check terminal logs)

**If all items are checked, you're ready to use the Medical Chatbot!** 🎉
