# Training Data vs Evaluation Data - Are They the Same?

## Short Answer: **NO ❌ - They Are Different**

The training data and evaluation data are **completely separate datasets** used for different purposes.

---

## Training Data (Knowledge Base)

### What is it?
Documents and datasets **indexed into Pinecone** that the chatbot learns from and searches through.

### Source Files
Located in `Data/` directory:

```
📁 Data/
├── The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf    ← Indexed
├── medquad_dataset.json                             ← Indexed
├── medical_conditions.json                          ← Indexed + Ingested
├── medical_diseases.csv                             ← Indexed + Ingested
└── mimic_iv_reference.json                          ← Indexed + Ingested
```

### How It's Used
```
1. Loaded by: store_index.py
2. Processing: load_mixed_data() → text_split() → chunk creation
3. Stored in: Pinecone vector database (index: "medicalbot")
4. Retrieved by: RAG retriever during chat queries
```

### How Stored
- Split into **chunks** (~500-1000 tokens each)
- Converted to **embeddings** (384-dim vectors)
- Stored in **Pinecone** with metadata
- Searched via **semantic similarity**

### Purpose
✅ **Training/Knowledge Base** - What the chatbot "knows"

---

## Evaluation Data (Test Set)

### What is it?
Q&A pairs used to **test how well the chatbot performs**, completely independent of training data.

### Source File
Located in `docs/evaluation/`:

```
📁 docs/evaluation/
├── qa_dataset.json              ← Evaluation questions
├── qa_dataset_expanded.json     ← Extended evaluation questions
├── evaluate_with_visualization.py
└── ragas_results.csv            ← Evaluation results
```

### Format
Each Q&A pair:
```json
{
  "question": "What are common symptoms of diabetes?",
  "ground_truth": "Symptoms include frequent urination, thirst, weight loss..."
}
```

### How It's Used
```
1. Loaded by: evaluate_with_visualization.py
2. For each Q&A pair:
   a) Query RAG system with the question
   b) Get the chatbot's answer
   c) Compare answer vs ground truth
   d) Calculate RAGAS metrics
3. Metrics computed:
   - Faithfulness (is answer supported by context?)
   - Answer Relevancy (is answer relevant to question?)
   - Context Precision (are retrieved docs relevant?)
   - Context Recall (do retrieved docs cover ground truth?)
```

### Purpose
✅ **Evaluation/Testing** - How well does the chatbot perform?

---

## Key Differences

| Aspect | Training Data | Evaluation Data |
|--------|---------------|-----------------|
| **Location** | `Data/` | `docs/evaluation/` |
| **Format** | PDFs, JSON, CSV | Q&A JSON pairs |
| **Storage** | Pinecone vectors | Local JSON files |
| **How Used** | Searched by RAG | Tested for accuracy |
| **Purpose** | Knowledge base | Performance measurement |
| **Size** | ~100K+ tokens | 50-100 Q&A pairs |
| **Updated** | Rarely | Frequently for testing |
| **Used During** | Chat queries | Evaluation script |

---

## Data Separation Visualization

```
┌─────────────────────────────────────────────────────┐
│          MEDICAL CHATBOT SYSTEM                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  TRAINING/KNOWLEDGE BASE                           │
│  ┌──────────────────────────────────────────┐      │
│  │ Data/ directory:                         │      │
│  │ • GALE_ENCYCLOPEDIA.pdf                  │      │
│  │ • medquad_dataset.json                   │      │
│  │ • medical_conditions.json                │      │
│  │ • medical_diseases.csv                   │      │
│  │ • mimic_iv_reference.json                │      │
│  │                                          │      │
│  │ ↓ processed by store_index.py            │      │
│  │                                          │      │
│  │ Pinecone Index: "medicalbot"             │      │
│  │ (384-dim embeddings, searchable)         │      │
│  └──────────────────────────────────────────┘      │
│              ↓ (used for RAG retrieval)            │
│                                                     │
│  CHAT QUERIES                                      │
│  ┌──────────────────────────────────────────┐      │
│  │ User asks: "What is diabetes?"           │      │
│  │                                          │      │
│  │ RAG System:                              │      │
│  │ • Retrieves from Pinecone (training)    │      │
│  │ • Returns answer                         │      │
│  └──────────────────────────────────────────┘      │
│                                                     │
│  EVALUATION (SEPARATE)                             │
│  ┌──────────────────────────────────────────┐      │
│  │ docs/evaluation/qa_dataset.json:        │      │
│  │ • 50-100 test Q&A pairs                 │      │
│  │ • NOT from training data                │      │
│  │ • Used by evaluate_with_visualization  │      │
│  │ • Measures performance                  │      │
│  │ • Computes RAGAS metrics                │      │
│  └──────────────────────────────────────────┘      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Data Flow Comparison

### Training Flow
```
Data/ directory files
    ↓
load_mixed_data() [src/helper.py]
    ↓
text_split() [chunking]
    ↓
download_hugging_face_embeddings() [embedding model]
    ↓
PineconeVectorStore.from_documents()
    ↓
Pinecone Index ("medicalbot")
    ↓
(stays indexed for chat use)
```

### Evaluation Flow
```
qa_dataset.json [evaluation Q&A pairs]
    ↓
prepare_evaluation_data()
    ↓
For each Q&A:
  - Query RAG system
  - Get answer
  - Retrieve contexts
    ↓
build_rag_chain_for_eval()
    ↓
run_ragas_evaluation()
    ↓
RAGAS Metrics (faithfulness, relevancy, etc.)
    ↓
Visualization & Results
```

---

## Why Separate Datasets?

### ✅ Best Practice: Train/Test Split
Keeping datasets separate ensures:

1. **No Data Leakage** - Evaluation isn't biased by training data
2. **Fair Assessment** - Tests on unseen questions
3. **True Performance** - Measures real-world capability
4. **Generalization** - Shows if chatbot generalizes beyond training

### Example of Data Leakage (BAD)
```
If eval dataset = training dataset:
- Chatbot memorizes answers
- Metrics look artificially high
- Doesn't reflect real performance
- Invalid evaluation results ❌
```

### Proper Separation (GOOD)
```
Training: GALE Encyclopedia, medquad, medical datasets
Evaluation: Separate Q&A test set
Result: Valid, accurate performance metrics ✅
```

---

## Evaluation Dataset Details

### What Questions Are Asked?
Examples from `qa_dataset.json`:

```
1. "What are the common symptoms of diabetes mellitus?"
2. "How is hypertension typically treated?"
3. "What are the main risk factors for coronary heart disease?"
4. "How does aspirin work to prevent blood clots?"
5. "What are the typical treatments for community-acquired pneumonia?"
...and 45+ more questions
```

### How Are They Generated?
The questions are:
- ✅ **Independent** - Not from training documents
- ✅ **Medical** - But different topics than training
- ✅ **Diverse** - Cover symptoms, treatments, diagnoses
- ✅ **With answers** - Include "ground truth" answers

### Are They in Training Data?
- ❌ **NOT exactly** - Different wording, slightly different topics
- ✅ But related topics may be in training data
- This is **intentional** - Tests retrieval on related-but-unseen questions

---

## RAGAS Evaluation Process

### What Happens During Evaluation?

```
For each evaluation Q&A pair:

1. Question: "What are symptoms of diabetes?"
   
2. RAG System searches Pinecone
   → Retrieves 8 chunks from training data
   
3. Chatbot generates answer
   → Uses retrieved chunks + LLM
   
4. Compare:
   - LLM's answer
   - Retrieved contexts
   - Ground truth answer
   
5. Compute Metrics:
   - Faithfulness: Is answer loyal to retrieved text?
   - Answer Relevancy: How relevant to question?
   - Context Precision: Are retrieved chunks relevant?
   - Context Recall: Do chunks cover ground truth?
   
6. Results recorded
```

---

## Results: How Performance is Measured

### Before Integration
```
Metrics based on:
- GALE Encyclopedia
- medquad dataset
- Initial indexed documents
```

### After MIMIC-IV Integration
```
Metrics based on:
- All previous sources PLUS
- MIMIC-IV reference data added
```

### Comparison Shows
- Did adding MIMIC-IV improve performance?
- How much better are answers?
- Which metrics improved most?

---

## Key Facts

| Fact | Details |
|------|---------|
| **Separate?** | Yes, completely independent |
| **Training Location** | `Data/` directory + Pinecone |
| **Evaluation Location** | `docs/evaluation/qa_dataset.json` |
| **Size** | Training: ~100K tokens, Eval: 50-100 pairs |
| **Used During** | Training: Chat queries, Eval: Testing script |
| **Overlap?** | No - prevents data leakage |
| **Fair?** | Yes - valid evaluation methodology |

---

## Summary

### Training Data (Indexed in Pinecone)
- GALE Encyclopedia + medical datasets
- Used during chat queries
- Provides knowledge for RAG

### Evaluation Data (Q&A Test Set)
- Separate Q&A pairs
- Used to measure performance
- Generates RAGAS metrics

### Result
✅ **Valid Evaluation** - Separate datasets ensure accurate performance measurement
✅ **No Data Leakage** - Chatbot tested on unseen questions
✅ **Fair Metrics** - Results reflect true capabilities

---

**Status**: ✅ Properly Separated  
**Risk**: ❌ No data leakage  
**Validity**: ✅ High confidence in metrics

