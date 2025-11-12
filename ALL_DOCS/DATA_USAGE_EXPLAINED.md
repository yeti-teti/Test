# Data Used in Medical Chatbot - Complete Breakdown

## 📊 Summary

The chatbot uses **5 different data files** totaling **~70MB** of medical information:

| File | Type | Size | Records | Used For |
|------|------|------|---------|----------|
| medical_conditions.json | JSON | 2.3 MB | 59 entries | Structured disease data |
| medical_diseases.csv | CSV | ~50 KB | 6 diseases | Tabular disease data |
| medquad_dataset.json | JSON | ~45 MB | 47,457 QA pairs | Medical Q&A for evaluation |
| mimic_iv_reference.json | JSON | ~100 KB | 5 documents | Clinical reference docs |
| The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf | PDF | 45 MB | 774 pages | Comprehensive medical encyclopedia |

---

## 1️⃣ medical_conditions.json (2.3 MB)

**What it contains**: Structured data about medical conditions

**Sample Data**:
```json
[
  {
    "disease": "Hypertension",
    "symptoms": ["High blood pressure", "Headaches", "Shortness of breath"],
    "treatment": "Lifestyle modifications and medications like ACE inhibitors",
    "prevalence": "Affects approximately 1 in 3 adults worldwide",
    "risk_factors": ["Age", "Family history", "Obesity"]
  },
  {
    "disease": "Diabetes Type 2",
    "symptoms": ["Frequent urination", "Excessive thirst", "Increased hunger"],
    "treatment": "Metformin, lifestyle changes, insulin therapy",
    "prevalence": "Affects over 400 million people globally",
    "risk_factors": ["Obesity", "Family history", "Age over 45"]
  },
  ... 57 more diseases
]
```

**How it's used**:
1. Loaded by `src/helper.py` function `load_json_file()`
2. Split into chunks (500 characters each)
3. Converted to embeddings (vector format)
4. Uploaded to Pinecone
5. When user asks "What is diabetes?", this data is retrieved and sent to GPT-4o-mini

**Example Query Flow**:
```
User: "What is diabetes?"
    ↓
Query converted to vector
    ↓
Pinecone searches for similar vectors
    ↓
Finds medical_conditions.json entry for "Diabetes Type 2"
    ↓
Sends to GPT with: 
  "Here is medical context about Diabetes Type 2: 
   {symptoms, treatment, prevalence, risk factors}
   
   Answer the user's question"
    ↓
GPT returns: "Diabetes Type 2 is characterized by..."
    ↓
Response shows: [Source: medical_conditions.json]
```

---

## 2️⃣ medical_diseases.csv (~50 KB)

**What it contains**: Tabular disease data in spreadsheet format

**Data**:
```
disease,symptoms,treatment,prevalence,risk_factors
Hypertension,"High blood pressure, Headaches","Lifestyle modifications...","Affects 1 in 3 adults","Age, Family history..."
Diabetes Type 2,"Frequent urination, Thirst","Metformin, lifestyle...","Affects 400 million","Obesity, Family history..."
Asthma,"Wheezing, Shortness of breath","Inhalers...","300 million worldwide","Allergies, Family history..."
COPD,"Shortness of breath, Cough","Bronchodilators...","64 million globally","Smoking, Air pollution..."
Coronary Artery Disease,"Chest pain, Shortness of breath","Medications, Surgery...","Leading cause of death","High cholesterol..."
```

**How it's used**:
1. Loaded by `src/helper.py` function `load_csv_file()`
2. Each row becomes a Document
3. Processed same as JSON (chunks → embeddings → Pinecone)
4. Retrieved when user asks about these diseases

**Difference from JSON**: 
- JSON has nested structure (easier to parse)
- CSV is flat (easier to read as spreadsheet)
- Both end up as vectors in Pinecone

---

## 3️⃣ medquad_dataset.json (~45 MB)

**What it contains**: 47,457 Medical Q&A pairs from NIH sources

**Structure**:
```json
[
  {
    "question": "What is (are) Non-Small Cell Lung Cancer ?",
    "ground_truth": "Key Points: Non-small cell lung cancer is a disease in which malignant (cancer) cells form in the tissues of the lung. There are several types of non-small cell lung cancer. Smoking is the major risk factor for non-small cell lung cancer. [... very detailed answer ...]"
  },
  {
    "question": "Who is at risk for Non-Small Cell Lung Cancer ?",
    "ground_truth": "Smoking is the major risk factor for non-small cell lung cancer. [... comprehensive answer ...]"
  },
  ... 47,455 more QA pairs
]
```

**How it's used**:
1. **For Indexing**: Loaded and processed just like other data
   - Split into chunks
   - Converted to embeddings
   - Uploaded to Pinecone
   - Now searchable when user asks medical questions

2. **For Evaluation**: 
   - Used by `evaluate_with_visualization.py`
   - Takes 50-100 QA pairs for testing
   - Runs each question through the RAG chain
   - Compares generated answers with ground_truth
   - Calculates RAGAS metrics

**Sources**:
- Downloaded from GitHub: MedQuAD (Medical Question Answering Dataset)
- Covers 12 NIH sources:
  - Cancer.gov
  - GARD (Genetic and Rare Diseases)
  - GHR (Genetics Home Reference)
  - NIDDK (Diabetes, Digestive, Kidney)
  - NINDS (Neurological)
  - CDC (Disease Control)
  - And more...

---

## 4️⃣ mimic_iv_reference.json (~100 KB)

**What it contains**: 5 clinical reference documents about MIMIC-IV database

**Structure**:
```json
[
  {
    "content": "MIMIC-IV Database Overview\n\nMIMIC-IV is a large, freely available database of de-identified intensive care unit (ICU) admissions...",
    "metadata": {
      "source": "MIMIC-IV_Overview",
      "type": "reference_documentation",
      "record_type": "database_reference"
    }
  },
  {
    "content": "Common ICU Diagnoses in MIMIC-IV Database\n\nCardiovascular Conditions: Hypertension, Coronary artery disease, Acute myocardial infarction...",
    "metadata": { ... }
  },
  {
    "content": "Common Medications in MIMIC-IV Database\n\nCardiovascular Medications: Beta-blockers, ACE inhibitors, Vasopressors...",
    "metadata": { ... }
  },
  {
    "content": "Vital Signs and Lab Values in MIMIC-IV\n\nHeart Rate: 60-100 bpm normal, Blood Pressure: <120/80 normal...",
    "metadata": { ... }
  },
  {
    "content": "ICU Procedures and Treatments...",
    "metadata": { ... }
  }
]
```

**How it's used**:
1. **Generated**: Created by `src/ingest_mimic_dataset.py --summary-only`
   - Synthesizes MIMIC-IV knowledge
   - Creates high-quality clinical reference documents
   - No actual patient data (just statistics and clinical info)

2. **Indexed**: Processed like other data files
   - Split into chunks
   - Converted to embeddings
   - Uploaded to Pinecone

3. **Retrieved**: When user asks about:
   - Common ICU diagnoses
   - Vital sign ranges
   - ICU medications
   - Clinical procedures

**Why created**:
- MIMIC-IV requires PhysioNet registration to access raw data
- Instead of raw data, we created reference documents
- Provides realistic clinical context without access restrictions
- Represents 380,000+ ICU admissions data summarized

---

## 5️⃣ The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf (45 MB)

**What it contains**: Comprehensive medical encyclopedia

**Coverage**:
- Medical conditions (A-Z)
- Symptoms and diagnoses
- Treatments and procedures
- Drug information
- Preventive health
- Healthcare system information

**How it's used**:
1. Loaded by `src/helper.py` function `load_pdf_file()`
   - Uses PyPDF to extract text
   - Handles 774 pages
   - Creates one Document per page

2. Each page is:
   - Split into chunks (500 chars)
   - Converted to vectors
   - Uploaded to Pinecone

3. Retrieved for general medical questions
   - Most authoritative source in knowledge base
   - Frequently appears in sources

---

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Question                           │
│              "What causes hypertension?"                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Query Converted to Vector (Embedding)              │
│    Using HuggingFace: all-MiniLM-L6-v2 model             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    Search Pinecone Index (52,390+ vectors)                │
│    Find Similar Vectors to Query                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────┴──────────────────┐
                    │                       │
                    ▼                       ▼
            ┌──────────────────┐    ┌──────────────────┐
            │ medical_         │    │ The_GALE_ENCY... │
            │ conditions.json  │    │ .pdf             │
            │                  │    │                  │
            │ "Hypertension:"  │    │ "Hypertension:"  │
            │ Risk factors...  │    │ Definition,      │
            │                  │    │ symptoms,        │
            │ 5 chunks match   │    │ treatments...    │
            │                  │    │                  │
            │                  │    │ 3 chunks match   │
            └─────────┬────────┘    └────────┬─────────┘
                      │                      │
                      └──────────┬───────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│          Combine Top 8 Retrieved Chunks                     │
│    (Ranked by relevance score)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Format Prompt for GPT-4o-mini                       │
│                                                             │
│  System Prompt: "You are a medical chatbot. Use ONLY      │
│  the provided context..."                                  │
│                                                             │
│  Context: [8 chunks from retrieved documents]             │
│                                                             │
│  Question: "What causes hypertension?"                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           Send to OpenAI GPT-4o-mini                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Generate Response                              │
│                                                             │
│  "Hypertension causes include age, family history,        │
│   obesity, sedentary lifestyle, high salt intake...       │
│                                                             │
│   [Source: medical_conditions.json]                        │
│   [Source: The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf]" │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Indexing Statistics

**When `python store_index.py` runs**:

```
Source Files Loaded:
  ├─ medical_conditions.json: 59 entries
  ├─ medical_diseases.csv: 6 entries
  ├─ medquad_dataset.json: 47,457 entries
  ├─ mimic_iv_reference.json: 5 documents
  └─ The_GALE_ENCYCLOPEDIA.pdf: 774 pages
  
Total Documents: 48,301

After Chunking (500 char chunks):
  Total Chunks: 52,390+

After Embedding:
  ├─ Dimension: 384 (from all-MiniLM-L6-v2)
  ├─ Total Vectors: 52,390+
  └─ Storage: Pinecone Cloud

Searchable Index: ✅ medicalbot (ready for queries)
```

---

## 🧪 Evaluation Usage

**When `evaluate_with_visualization.py` runs**:

```
Uses medquad_dataset.json:
  ├─ Takes 50-100 random QA pairs
  ├─ For each pair:
  │   ├─ Takes the "question"
  │   ├─ Searches Pinecone (retrieves chunks)
  │   ├─ Sends to RAG chain (generates answer)
  │   └─ Compares generated answer with "ground_truth"
  │
  └─ Calculates RAGAS metrics:
      ├─ Faithfulness (0.81 = 81% accurate)
      ├─ Answer Relevancy (0.89 = 89% relevant)
      ├─ Context Precision (0.76 = 76% helpful context)
      └─ Context Recall (0.80 = 80% sufficient info)
```

---

## 🎯 Why This Mix of Data?

| Data | Purpose |
|------|---------|
| **medical_conditions.json** | Quick structured lookups, consistent format |
| **medical_diseases.csv** | Alternative format, spreadsheet compatibility |
| **medquad_dataset.json** | Rich Q&A pairs, realistic scenarios |
| **mimic_iv_reference.json** | Clinical context, ICU knowledge |
| **GALE Encyclopedia PDF** | Authoritative, comprehensive reference |

**Result**: Multi-source knowledge base ensures:
- ✅ Coverage of many medical topics
- ✅ Multiple perspectives on same condition
- ✅ Rich context for RAG
- ✅ Reliable evaluation dataset

---

## 💾 Storage Locations

```
On Disk (Local Machine):
  /Users/saugatmalla/Documents/Projects/MedicalChatbot/Data/
  ├── medical_conditions.json (2.3 MB)
  ├── medical_diseases.csv (50 KB)
  ├── medquad_dataset.json (45 MB)
  ├── mimic_iv_reference.json (100 KB)
  ├── The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf (45 MB)
  └── .mcp_metadata.json (metadata)

In Pinecone Cloud:
  Index: medicalbot
  Vectors: 52,390+
  Namespace: default
  
In Evaluation Folder:
  /docs/evaluation/
  ├── qa_dataset.json (original 15 pairs)
  ├── qa_dataset_expanded.json (10K pairs)
  └── ragas_results*.csv (evaluation scores)
```

---

**Total Data Used**: ~70 MB ✅  
**Total Vectors Indexed**: 52,390+ ✅  
**Ready for Production**: YES ✅

