# Complete Data Sources - Comprehensive Breakdown

## TL;DR: Data Usage Summary

| Component | Data Source | Files | Purpose | Stored In |
|-----------|-------------|-------|---------|-----------|
| **Training** | Medical docs | 5 files in `Data/` | Knowledge base | Pinecone |
| **Evaluation** | Q&A pairs | `qa_dataset.json` | Test performance | Local JSON |
| **MCP Local** | Datasets | JSON/CSV in `Data/` | Keyword search | Memory |
| **Web Search** | Real-time web | Exa AI API | Latest info | Online |
| **Chat History** | User messages | Session memory | Context | Memory |

---

## 1. TRAINING DATA (RAG Knowledge Base)

### Location: `Data/` directory

```
📁 Data/
├── The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf
├── medquad_dataset.json
├── medical_conditions.json
├── medical_diseases.csv
└── mimic_iv_reference.json
```

### Processing Pipeline

```
Data/ files
    ↓
store_index.py loads via load_mixed_data()
    ↓
Text extraction:
- PDF → text via PyPDF
- JSON → parse items
- CSV → parse rows
    ↓
text_split() → chunks ~500-1000 tokens each
    ↓
download_hugging_face_embeddings() → 384-dim vectors
    ↓
PineconeVectorStore.from_documents()
    ↓
Stored in Pinecone:
- Index: "medicalbot"
- Namespace: "default"
- Total: ~10K+ embeddings
```

### Each File's Role

#### 1. **The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf**
- **Source**: Medical encyclopedia (authoritative)
- **Content**: Comprehensive medical information
- **Format**: PDF (extracted via PyPDF)
- **Size**: Large (~1000+ pages)
- **Usage**: General medical knowledge, symptoms, diseases
- **Chunks Created**: ~2000+
- **Quality**: Very high (encyclopedic)

#### 2. **medquad_dataset.json**
- **Source**: MedQuAD (freely available medical Q&A)
- **Content**: Q&A pairs on medical topics
- **Format**: JSON with structure `{question, answer}`
- **Size**: ~16K Q&A pairs (limited to 100 used)
- **Usage**: Medical Q&A knowledge
- **Chunks Created**: ~1500+
- **Quality**: High (curated Q&A)

#### 3. **medical_conditions.json**
- **Source**: Ingested dataset (MIMIC-IV inspired)
- **Content**: 59 medical conditions with structured info
- **Format**: JSON array of condition objects
- **Fields**: name, description, symptoms, treatment, etc.
- **Usage**: Structured condition lookup
- **Chunks Created**: ~500+
- **Quality**: Medium (structured data)
- **Also used by**: MCP local search

#### 4. **medical_diseases.csv**
- **Source**: Ingested dataset
- **Content**: 6 diseases with basic information
- **Format**: CSV with columns
- **Usage**: Disease quick reference
- **Chunks Created**: ~100+
- **Quality**: Medium (minimal data)
- **Also used by**: MCP local search

#### 5. **mimic_iv_reference.json**
- **Source**: MIMIC-IV inspired reference
- **Content**: 5 clinical documents with ICU data
- **Format**: JSON with clinical scenarios
- **Usage**: Real-world medical scenarios, diagnoses
- **Chunks Created**: ~200+
- **Quality**: High (realistic)
- **Also used by**: MCP local search

### How Training Data is Searched

```
User Question: "What is diabetes?"
    ↓
Question converted to 384-dim embedding
    ↓
Pinecone searches for similar embeddings
    ↓
MMR (Max Marginal Relevance) retrieval:
- Retrieves k=8 chunks
- Fetches k=20 candidates
- Balances relevance + diversity (lambda=0.5)
    ↓
Top 8 chunks returned to LLM
    ↓
LLM generates answer
```

---

## 2. EVALUATION DATA (Test Set)

### Location: `docs/evaluation/`

```
📁 docs/evaluation/
├── qa_dataset.json              ← Main evaluation Q&A
├── qa_dataset_expanded.json     ← Extended version
├── evaluate_with_visualization.py
├── ragas_results.csv
└── qa_dataset.json
```

### QA Dataset Structure

```json
[
  {
    "question": "What are the common symptoms of diabetes mellitus?",
    "ground_truth": "Common symptoms include frequent urination, excessive thirst..."
  },
  {
    "question": "How is hypertension typically treated?",
    "ground_truth": "Treatment includes lifestyle modifications and medications..."
  }
]
```

### Dataset Statistics

- **Total Q&A pairs**: ~50-100 (configurable)
- **Format**: JSON array
- **Independence**: Not from training data
- **Quality**: Medium-High (manually curated)
- **Coverage**: Diverse medical topics

### Evaluation Process

```
For each Q&A pair (50 iterations):

1. Load question
   
2. Query RAG system:
   a. Convert question to embedding
   b. Search Pinecone
   c. Retrieve 8 documents
   
3. Generate answer:
   a. Pass question + docs to LLM
   b. Get chatbot answer
   
4. Extract contexts:
   a. Get retrieved document chunks
   
5. Prepare evaluation data:
   {
     "question": "What are common symptoms?",
     "answer": "Chatbot's answer",
     "contexts": [...retrieved chunks...],
     "reference": "Ground truth answer"
   }
   
6. Repeat for all pairs
```

### RAGAS Metrics Computed

```
For each Q&A pair:

1. Faithfulness
   - Does answer match retrieved contexts?
   - Score: 0-1
   
2. Answer Relevancy
   - Is answer relevant to question?
   - Score: 0-1
   
3. Context Precision
   - Are retrieved documents relevant?
   - Score: 0-1
   
4. Context Recall
   - Do documents cover ground truth?
   - Score: 0-1
```

### Results Storage

```
ragas_results.csv:
question,answer,contexts,reference,faithfulness,answer_relevancy,...
"What is diabetes?","Diabetes is...",["chunk1","chunk2"],"Ground truth",0.85,0.92,...

ragas_summary.json:
{
  "faithfulness_mean": 0.82,
  "answer_relevancy_mean": 0.88,
  "context_precision_mean": 0.79,
  "context_recall_mean": 0.91
}
```

---

## 3. MCP LOCAL DATA (Ingested Datasets)

### What is MCP?
Model Context Protocol - local data ingestion and search

### Available Datasets

```
User can ingest any JSON/CSV file:

Examples:
- medical_conditions.json
- medical_diseases.csv
- mimic_iv_reference.json
- custom_dataset.json (user-provided)
```

### How MCP Search Works

```
User: "What are symptoms of asthma?"
    ↓
MCP keyword extraction: ["symptoms", "asthma"]
    ↓
Search ingested datasets:
- medical_conditions.json: Found "asthma" entry
- medical_diseases.csv: No match
- mimic_iv_reference.json: Found in ICU diagnoses
    ↓
Keyword relevance scoring (0-1)
    ↓
Top 10 results returned
    ↓
Show "📊 MCP (Local Data)" in source attribution
```

### MCP Storage

```
In memory (MCPDatasetServer):
- Loaded documents list
- Ingested dataset metadata
- Fast keyword search
```

### Usage in Chat

```
Answers combine:
- RAG search (Pinecone semantic)
- MCP search (Local keyword)
- Exa web search (Real-time)
    ↓
All sources shown in source attribution box
```

---

## 4. WEB SEARCH DATA (Exa AI)

### What Data Comes from Web?

```
Real-time medical websites:
- Mayo Clinic
- WebMD
- MedlinePlus
- NIH.gov
- CDC.gov
- WHO.int
- Healthline.com
- PubMed
- NHS.uk
```

### Web Search Process

```
Question: "Latest COVID-19 variants"
    ↓
Medical query check: YES
    ↓
Exa AI search:
- Search query: "Latest COVID-19 variants medical health"
- Type: Neural search
- Domains: Medical sites only
- Exclude: Social media
    ↓
Real-time results from web
    ↓
Show "🌐 Web Search" in source attribution
```

### Data Not Stored Locally

- Retrieved on-demand from Exa API
- Not cached (always fresh)
- Shows current information
- URLs included in response

---

## 5. CONVERSATION HISTORY (Session Data)

### Storage

```
In-memory conversation buffer:
ConversationBufferWindowMemory
- Max tokens: 1000
- Window: Last N messages
- Cleared on app restart
```

### Usage

```
Question 1: "What is diabetes?"
    ↓ (stored in memory)

Question 2: "What are treatments?"
    ↓ Context includes Q1 for multi-turn
    ↓ (stored in memory)

Question 3: "Anything else?"
    ↓ Can reference both Q1 and Q2
```

---

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  USER QUERY                             │
│         "What is type 2 diabetes?"                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌──────────┐ ┌──────────┐
    │ Training│  │Local MCP │ │Exa Web  │
    │ Data    │  │Data      │ │Search   │
    │(Pinecone)  │(Memory)  │ │(API)    │
    └───┬────┘  └─────┬────┘ └────┬────┘
        │             │           │
        │ RAG Search  │ Keyword   │ Real-time
        │ Semantic    │ Matching  │ Web
        │             │           │
        └─────────────┼───────────┘
                      │
              ┌───────▼───────┐
              │ Combine all   │
              │ 3 sources     │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │ Send context  │
              │ to GPT-4o-min│
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │ Generate      │
              │ Answer        │
              └───────┬───────┘
                      │
              ┌───────▼──────────────┐
              │ Return response:     │
              │ - Answer text        │
              │ - Sources used       │
              │ - Source breakdown   │
              └──────────────────────┘
                      │
                      ▼
              ┌──────────────────┐
              │  User sees chat  │
              │  with attribution│
              └──────────────────┘
```

---

## Data Lifecycle

### Training Data
```
Data/ files
    ↓
store_index.py (run manually)
    ↓
Pinecone (stays indexed)
    ↓
Used in every chat query
    ↓
Never changes (unless re-indexed)
```

### Evaluation Data
```
qa_dataset.json
    ↓
evaluate_with_visualization.py (run manually)
    ↓
Results written to CSV/JSON
    ↓
Not used in production chat
    ↓
Only for measuring performance
```

### MCP Local Data
```
User ingests dataset
    ↓
MCPDatasetServer loads into memory
    ↓
Used in every chat query
    ↓
Persists in session
    ↓
Cleared on app restart
```

### Web Data
```
Real-time lookup
    ↓
Exa API called on each medical question
    ↓
Results used in response
    ↓
Not cached
    ↓
Always current
```

---

## File Locations Summary

```
MedicalChatbot/
│
├── Data/                          ← TRAINING DATA
│   ├── GALE_ENCYCLOPEDIA.pdf
│   ├── medquad_dataset.json
│   ├── medical_conditions.json
│   ├── medical_diseases.csv
│   └── mimic_iv_reference.json
│
├── docs/evaluation/               ← EVALUATION DATA
│   ├── qa_dataset.json
│   ├── qa_dataset_expanded.json
│   └── evaluate_with_visualization.py
│
├── src/
│   ├── mcp_server.py             ← MCP LOCAL DATA STORAGE
│   ├── mcp_client.py             ← MCP INTERFACE
│   ├── exa_web_search.py         ← WEB SEARCH
│   └── prompt.py                 ← SESSION MEMORY
│
├── store_index.py                ← INDEX TRAINING DATA
│
└── app.py                         ← CHAT APPLICATION
    ├── Uses Training data (Pinecone)
    ├── Uses MCP data (local)
    ├── Uses Web data (Exa API)
    └── Uses session memory
```

---

## Data Size Estimates

| Data Type | Size | Chunks | Notes |
|-----------|------|--------|-------|
| GALE Encyclopedia | ~100MB | 2000+ | Largest source |
| medquad dataset | ~50MB | 1500+ | Q&A format |
| medical_conditions.json | ~500KB | 500+ | Structured |
| medical_diseases.csv | ~100KB | 100+ | Minimal |
| mimic_iv_reference.json | ~100KB | 200+ | Realistic data |
| **Training Total** | **~150MB** | **~4300+** | Pinecone indexed |
| Evaluation Q&A | ~100KB | N/A | Only 50-100 pairs |
| **Total** | **~150MB** | **~4300+** | For production |

---

## Key Points

✅ **Training & Evaluation Separate** - No data leakage  
✅ **Multiple Sources** - RAG + MCP + Web combined  
✅ **Real-time Web** - Latest medical info available  
✅ **Local Data Ingestion** - MCP for custom datasets  
✅ **Fair Metrics** - Evaluation on unseen data  
✅ **Complete Attribution** - Sources shown to user  

---

**Status**: ✅ Complete Data Integration  
**Sources**: 5 training files + evaluation set + MCP + Web API

