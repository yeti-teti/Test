# Dataset Ingestion - Complete Explanation

## What is "Ingest"?

**Ingest** = Load and store third-party datasets into the system for use in MCP (Model Context Protocol) keyword search.

It's different from **indexing** (Pinecone):
- **Indexing**: Convert docs to vectors → Store in Pinecone (semantic search)
- **Ingesting**: Load datasets into memory → Store for keyword search (MCP)

---

## Two Purposes of Ingestion

### 1. **MCP Local Search** (Via ingest_dataset.py)
```
Load dataset file
    ↓
Store in MCP server memory
    ↓
Enable keyword search
    ↓
Return results in chat
```

### 2. **Pinecone Indexing** (Via store_index.py)
```
Load from Data/ directory
    ↓
Chunk into smaller pieces
    ↓
Convert to embeddings
    ↓
Store in Pinecone
    ↓
Enable semantic search
```

---

## How Ingestion Works

### Step 1: Run Ingest Command

```bash
python ingest_dataset.py Data/medical_conditions.json json
```

### Step 2: File Detection

```python
# Lines 101-131 in mcp_server.py
def ingest_dataset(self, file_path: str, format_type: str = None):
    
    file_path_obj = Path(file_path)
    
    # Auto-detect format if not specified
    if format_type == 'auto':
        format_type = file_path_obj.suffix[1:].lower()
        # .json → 'json'
        # .csv → 'csv'
        # .pdf → 'pdf'
```

### Step 3: Load File Based on Format

```python
if format_type == 'json':
    documents = load_json_file(str(file_path_obj))
    
elif format_type == 'csv':
    documents = load_csv_file(str(file_path_obj))
    
elif format_type == 'pdf':
    documents = load_pdf_file(str(file_path_obj))
```

### Step 4: Store in Memory

```python
# Store documents in class-level storage
self.documents.extend(documents)  # Persistent across instances

# Create metadata
metadata = DatasetMetadata(
    name=file_path_obj.stem,
    source_path=str(file_path_obj),
    format=format_type,
    record_count=len(documents),
    ingestion_date=datetime.now().isoformat()
)

# Add to ingested datasets list
self.ingested_datasets.append(metadata)
```

### Step 5: Persist to Disk

```python
# Save metadata to disk
self._save_metadata_to_disk()
# File: Data/.mcp_metadata.json
```

### Step 6: Ready for Search

```python
# Now available for keyword search
# MCP can search ingested datasets
```

---

## Ingestion Data Flow

```
┌─────────────────────────────────────────────────────┐
│          User runs ingest command                   │
│  python ingest_dataset.py Data/medical_conditions.json
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│     ingest_dataset.py processes arguments          │
│     • file_path: Data/medical_conditions.json      │
│     • format_type: json                            │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│     MedicalDatasetMCPServer.ingest_dataset()       │
│     1. Check file exists                           │
│     2. Detect format (.json → json)               │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│     Load file based on format                      │
│     • load_json_file()                             │
│     • load_csv_file()                              │
│     • load_pdf_file()                              │
│     → Extracts documents from file                 │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│     Store documents                                │
│     self.documents.extend(documents)               │
│     → In memory (class-level storage)              │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│     Create metadata                                │
│     • name: medical_conditions                     │
│     • format: json                                 │
│     • record_count: 59                             │
│     • ingestion_date: 2025-01-01...               │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│     Save to disk                                   │
│     File: Data/.mcp_metadata.json                 │
│     → Persist ingestion metadata                   │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│     Available for MCP search                       │
│     • Keyword search enabled                       │
│     • Used in chat responses                       │
│     • Shows in source attribution                  │
└─────────────────────────────────────────────────────┘
```

---

## What Files Can Be Ingested?

### JSON Format
```json
[
  {
    "name": "Diabetes",
    "description": "Type 2 diabetes...",
    "symptoms": "Frequent urination...",
    "treatment": "Metformin..."
  },
  {
    "name": "Hypertension",
    ...
  }
]
```

**Load via**: `load_json_file()`

### CSV Format
```
name,description,symptoms
"Diabetes","Type 2 diabetes...","Frequent urination..."
"Hypertension","High blood pressure...","Headaches..."
```

**Load via**: `load_csv_file()`

### PDF Format
```
Medical document with text content
```

**Load via**: `load_pdf_file()`

---

## Currently Ingested Datasets

### In Data/ Directory:

```
📁 Data/
├── medical_conditions.json
│   └─ 59 medical conditions with full descriptions
│
├── medical_diseases.csv
│   └─ 6 diseases with basic info
│
└── mimic_iv_reference.json
    └─ 5 clinical documents with realistic ICU scenarios
```

### Metadata Stored In:
```
📁 Data/
└── .mcp_metadata.json
    └─ Tracks ingestion history and dataset info
```

---

## Usage in Chat System

### Before Ingestion (Without MCP)

```
User: "What is diabetes?"
    ↓
Only searches:
├─ Pinecone (GALE, medquad)
└─ Exa Web

Answer missing:
❌ Local dataset info
```

### After Ingestion (With MCP)

```
User: "What is diabetes?"
    ↓
Searches:
├─ Pinecone (GALE, medquad)
├─ MCP (medical_conditions.json) ← NEW
└─ Exa Web

Answer includes:
✅ Local dataset info
✅ Structured data
✅ Better coverage
```

---

## Command Line Usage

### 1. Ingest a Dataset

```bash
# Auto-detect format
python ingest_dataset.py Data/medical_conditions.json

# Specify format
python ingest_dataset.py Data/medical_diseases.csv csv

# PDF format
python ingest_dataset.py docs/medical_guide.pdf pdf
```

**Output**:
```
✓ Dataset ingested successfully!
  Name: medical_conditions
  Format: json
  Records: 59
  Total documents: 59

Note: Run 'python store_index.py' to update the vector index.
```

### 2. List Ingested Datasets

```bash
python ingest_dataset.py --list
```

**Output**:
```
Found 3 ingested dataset(s):
  - medical_conditions (json, 59 records)
  - medical_diseases (csv, 6 records)
  - mimic_iv_reference (json, 5 records)
```

### 3. Start MCP Server

```bash
python ingest_dataset.py --mcp-server
```

**Output**:
```
Starting MCP server on stdio... (waiting for MCP client)
```

---

## How MCP Search Uses Ingested Data

### After Ingestion:

```python
# In mcp_server.py
class MedicalDatasetMCPServer:
    def __init__(self):
        self.documents = []  # Ingested documents stored here
        self.ingested_datasets = []  # Metadata stored here
```

### Search Process:

```python
# In mcp_server.py - search_documents()
def search_documents(self, query: str, dataset_name: str = None):
    """Search ingested documents for relevant content."""
    
    results = []
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    for doc in self.documents:  # ← Ingested documents
        content_lower = doc.page_content.lower()
        
        # Count matching keywords
        matching_words = sum(1 for word in query_words 
                           if word in content_lower)
        
        if matching_words > 0:
            # Calculate relevance
            relevance = matching_words / len(query_words)
            doc.metadata['relevance_score'] = relevance
            results.append(doc)
    
    # Sort by relevance
    results.sort(key=lambda x: x.metadata['relevance_score'], 
                 reverse=True)
    
    return results[:10]  # Top 10 results
```

---

## Ingestion vs Indexing Comparison

| Aspect | **Ingestion (MCP)** | **Indexing (Pinecone)** |
|--------|-------------------|----------------------|
| **Purpose** | Keyword search | Semantic search |
| **Process** | Load file → Store in memory | Load → Chunk → Embed → Store |
| **Storage** | Memory + Metadata file | Pinecone cloud |
| **Search Type** | Keyword matching | Vector similarity |
| **Speed** | Instant | ~200ms |
| **Cost** | Free | Pinecone subscription |
| **Data** | Any format (JSON, CSV, PDF) | Text documents |
| **Persistence** | Metadata on disk | Remote database |
| **Usage** | MCP search in chat | Primary RAG system |

---

## Complete Workflow

### 1. Initial Setup
```
Data files exist
├─ medical_conditions.json
├─ medical_diseases.csv
└─ mimic_iv_reference.json
```

### 2. Ingest (Optional, For MCP Search)
```bash
python ingest_dataset.py Data/medical_conditions.json
# → Loads into memory
# → Creates .mcp_metadata.json
```

### 3. Index (Required, For RAG)
```bash
python store_index.py
# → Loads Data/ files
# → Creates embeddings
# → Stores in Pinecone
```

### 4. Chat Uses Both
```
User question
    ↓
Searches:
├─ Pinecone (via store_index) ← Indexed
├─ MCP (via ingest_dataset) ← Ingested
└─ Exa Web
    ↓
Combined answer with all sources
```

---

## Key Points

✅ **Ingestion** = Load datasets into MCP for keyword search  
✅ **Indexing** = Load documents into Pinecone for semantic search  
✅ **Different purposes** = Complementary search methods  
✅ **Both searchable** = Better answer coverage  
✅ **Automatic on startup** = MCP loads previously ingested data  

---

## Example Ingestion Scenario

### Scenario: Add New Medical Dataset

```bash
# 1. Get a new dataset (e.g., conditions.json)
wget https://medical-api.com/conditions.json

# 2. Ingest it
python ingest_dataset.py conditions.json json

# Output:
# ✓ Dataset ingested successfully!
#   Name: conditions
#   Format: json
#   Records: 100
#   Total documents: 100

# 3. Now available in MCP search
# Next time user asks about conditions,
# MCP will search this new dataset too!

# 4. (Optional) Also index for semantic search
python store_index.py

# Now both MCP and Pinecone have the data
```

---

## Summary

**Ingestion Purpose**:
1. **Load third-party datasets** into the system
2. **Enable keyword search** via MCP
3. **Augment answers** with local structured data
4. **Provide alternative search method** beyond semantic

**Result**: Richer, more comprehensive answers combining:
- Semantic search (Pinecone)
- Keyword search (MCP)
- Web search (Exa)

---

**Status**: ✅ Dataset ingestion fully implemented  
**Used For**: MCP local data search in chat  
**Benefits**: Better answer coverage + transparent source attribution

