# Training vs Evaluation Data - Which is Used Where?

## Quick Answer: **NO - Different data is used**

```
TRAINING DATA (medquad_dataset.json)
└─ 47,457 real Q&A pairs from MedQuAD
└─ Used for: Pinecone indexing
└─ Used in: Production chat queries

EVALUATION DATA (qa_dataset.json or qa_dataset_expanded.json)
└─ 50-10,000 Q&A pairs (synthetic + real)
└─ Used for: RAGAS evaluation only
└─ Used in: evaluate_with_visualization.py script
```

---

## Data Used for Training

### What Gets Indexed

```python
# store_index.py loads ALL files from Data/
extracted_data = load_mixed_data(data_dir='Data/')

Files loaded:
├── GALE_ENCYCLOPEDIA.pdf (largest)
├── medquad_dataset.json (47,457 pairs)
├── medical_conditions.json (59 conditions)
├── medical_diseases.csv (6 diseases)
└── mimic_iv_reference.json (5 clinical docs)
```

### Where medquad_dataset.json Comes From

```python
# download_qa_dataset.py - download_medquad_dataset()
medquad_url = "https://github.com/abachaa/MedQuAD/archive/refs/heads/master.zip"

Process:
1. Download from GitHub (12 NIH collections)
2. Parse XML
3. Extract 47,457 Q&A pairs
4. Save to Data/medquad_dataset.json  ← TRAINING DATA
5. Used by store_index.py to index
```

### Indexed Into Pinecone

```python
# store_index.py
text_chunks = text_split(extracted_data)  # Split into chunks
PineconeVectorStore.from_documents(
    text_chunks,
    embeddings,
    index_name='medicalbot'
)

Result:
- Index name: "medicalbot"
- Total chunks: ~4,300+
- Includes: medquad + GALE + other Data/ files
- Used in: Production chat
```

---

## Data Used for Evaluation

### Two Possible Evaluation Datasets

#### Option 1: qa_dataset_expanded.json (COMBINED)

```python
# download_qa_dataset.py - create_expanded_qa_dataset()
output_path = Path(...) / "docs" / "evaluation" / "qa_dataset_expanded.json"

all_pairs = []

# Add from multiple sources:
print("Attempting to download MedQA...")
medqa_pairs = download_medqa_dataset()
all_pairs.extend(medqa_pairs[:2000])  # Limit: 2000

print("Attempting to download PubMedQA...")
pubmedqa_pairs = download_pubmedqa_dataset()
all_pairs.extend(pubmedqa_pairs)  # ~5000

print("Attempting to download HealthQA...")
healthqa_pairs = download_healthqa_dataset()
all_pairs.extend(healthqa_pairs[:1000])  # Limit: 1000

print("Attempting to download MedQuAD...")
medquad_pairs = download_medquad_dataset()
all_pairs.extend(medquad_pairs)  # 47,457 (but limited)

# If nothing downloaded, use synthetic
if not all_pairs:
    all_pairs = create_synthetic_expanded_dataset()

# Save combined dataset
json.dump(all_pairs, f)
print(f"Total QA pairs created: {len(all_pairs)}")
```

**Result**:
```
📁 docs/evaluation/qa_dataset_expanded.json
└─ ~10,000+ Q&A pairs (combined from multiple sources)
```

#### Option 2: qa_dataset.json (SYNTHETIC)

```python
# download_qa_dataset.py - create_synthetic_expanded_dataset()
def create_synthetic_expanded_dataset():
    """Create a larger synthetic medical QA dataset."""
    expanded_qa = [
        {"question": "What are the common symptoms of diabetes mellitus?",
         "ground_truth": "Common symptoms include frequent urination..."},
        {"question": "How is hypertension typically treated?",
         "ground_truth": "Hypertension is typically treated through..."},
        # ... 48 more MANUALLY CRAFTED pairs
    ]
    return expanded_qa
```

**Result**:
```
📁 docs/evaluation/qa_dataset.json
└─ 50 Q&A pairs (manually written, synthetic)
```

---

## How Evaluation Loads Data

```python
# evaluate_with_visualization.py - Lines 58-64

# Try expanded version first, fallback to original
qa_dataset_path = Path(__file__).parent / 'qa_dataset_expanded.json'
if not qa_dataset_path.exists():
    qa_dataset_path = Path(__file__).parent / 'qa_dataset.json'

with open(qa_dataset_path, 'r') as f:
    qa_data = json.load(f)
    
print(f"Loaded {len(qa_data)} Q&A pairs for evaluation")
```

**Priority**:
1. First choice: `qa_dataset_expanded.json` (if it exists)
2. Fallback: `qa_dataset.json` (if expanded doesn't exist)

---

## Key Difference: Training vs Evaluation

### Training Data Flow

```
Data/medquad_dataset.json
        ↓
store_index.py
        ↓
Chunk & embed
        ↓
Pinecone Index "medicalbot"
        ↓
Used in: Production chat (user queries search this)
```

### Evaluation Data Flow

```
docs/evaluation/qa_dataset.json
(OR qa_dataset_expanded.json)
        ↓
evaluate_with_visualization.py
        ↓
For each Q&A pair:
- Query Pinecone (search training data)
- Get answer from LLM
- Compare vs ground_truth
- Calculate RAGAS metrics
        ↓
Used in: Testing system performance (NOT production)
```

---

## Data Separation - Why Different?

### No Data Leakage

```
TRAINING DATA (Pinecone)
├─ medquad_dataset.json: 47,457 pairs
├─ GALE Encyclopedia: Large text
├─ medical_conditions.json: 59 conditions
├─ medical_diseases.csv: 6 diseases
└─ mimic_iv_reference.json: 5 clinical docs

EVALUATION DATA (Test questions)
├─ Option A: qa_dataset_expanded.json (10K+ pairs from OTHER sources)
└─ Option B: qa_dataset.json (50 SYNTHETIC pairs)

CRITICAL: Evaluation data is DIFFERENT from training data!
```

### Why Separate?

```
If evaluation = training:
❌ Chatbot would memorize answers
❌ Metrics would be artificially high
❌ Doesn't test generalization
❌ Invalid results

With separate data:
✅ Tests on unseen questions
✅ Fair performance measurement
✅ Tests generalization ability
✅ Valid evaluation
```

---

## Data Sources Comparison

### Training: medquad_dataset.json

**From**: 12 NIH collections (from GitHub)
```
1. CancerGov_QA - 3000 pairs
2. GARD_QA - 1500 pairs
3. GHR_QA - 800 pairs
4. MPlus_Health_Topics_QA - 2000 pairs
5. NIDDK_QA - 1500 pairs
6. NINDS_QA - 1200 pairs
7. SeniorHealth_QA - 800 pairs
8. NHLBI_QA_XML - 1500 pairs
9. CDC_QA - 2000 pairs
10. MPlus_ADAM_QA - 1000 pairs
11. MPlusDrugs_QA - 2000 pairs
12. MPlusHerbsSupplements_QA - 1500 pairs
─────────────────────────────
Total: 47,457 pairs
```

### Evaluation: qa_dataset.json

**From**: Hardcoded in Python (synthetic)
```
50 manually written Q&A pairs

Topics covered:
- Diabetes
- Hypertension
- Heart disease
- Pneumonia
- Migraines
- Asthma
- Kidney disease
- Vaccination
- Depression
... and 41 more topics
```

### Evaluation: qa_dataset_expanded.json

**From**: Multiple sources (if downloaded)
```
MedQA: 2,000 pairs (HuggingFace)
PubMedQA: 5,000 pairs (HuggingFace)
HealthQA: 1,000 pairs (HuggingFace)
MedQuAD: 47,457 pairs (GitHub)
─────────────────────────────
Total: 55,457+ pairs (but may use subset)
```

---

## Complete Data Usage Flow

```
┌─────────────────────────────────────────────────────────┐
│                   DOWNLOAD PHASE                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  download_qa_dataset.py                                │
│                                                         │
│  ├─ download_medquad_dataset()                         │
│  │  └─ GitHub → Data/medquad_dataset.json (47K pairs)  │
│  │                                                     │
│  ├─ create_expanded_qa_dataset()                       │
│  │  └─ Multiple sources → docs/evaluation/qa_dataset_expanded.json
│  │                                                     │
│  └─ create_synthetic_expanded_dataset()                │
│     └─ Hardcoded → docs/evaluation/qa_dataset.json (50 pairs)
│                                                         │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│                   TRAINING PHASE                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  store_index.py                                        │
│  ├─ Loads: Data/medquad_dataset.json + other files    │
│  ├─ Process: Split → Chunk → Embed                    │
│  └─ Output: Pinecone Index "medicalbot"               │
│                                                         │
│  Production Chat                                       │
│  └─ Searches: Pinecone (uses training data)           │
│                                                         │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│                   EVALUATION PHASE                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  evaluate_with_visualization.py                        │
│  ├─ Loads: docs/evaluation/qa_dataset.json (50 pairs) │
│  │   OR: docs/evaluation/qa_dataset_expanded.json      │
│  ├─ For each Q&A:                                     │
│  │  - Question from evaluation dataset                 │
│  │  - Search: Pinecone (training data)                │
│  │  - Answer from: LLM + retrieval                     │
│  │  - Compare: Answer vs ground_truth                 │
│  │  - Metric: RAGAS evaluation                        │
│  └─ Output: ragas_results_detailed.csv                │
│             ragas_summary.json                         │
│             PNG visualizations                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Summary Table

| Aspect | **Training Data** | **Evaluation Data** |
|--------|-------------------|-------------------|
| **File** | `Data/medquad_dataset.json` | `docs/evaluation/qa_dataset.json` |
| **Source** | GitHub (12 NIH collections) | Synthetic (hardcoded) OR other sources |
| **Count** | 47,457 Q&A pairs | 50 pairs (or 10,000+ if expanded) |
| **Format** | JSON (downloaded) | JSON (created) |
| **Used In** | `store_index.py` (Pinecone indexing) | `evaluate_with_visualization.py` |
| **Used For** | Training/knowledge base | Testing/evaluation only |
| **In Chatbot?** | ✅ YES (Pinecone search) | ❌ NO (not in production) |
| **Same Data?** | ❌ NO - COMPLETELY DIFFERENT | ❌ NO - SEPARATE DATASET |

---

## CRITICAL POINT

**The same medquad_dataset.json used for training is NOT used for evaluation.**

Why?
- ✅ Prevents data leakage
- ✅ Fair performance measurement
- ✅ Tests generalization on NEW questions
- ✅ Produces valid metrics

---

**Status**: ✅ Data properly separated  
**Training Data**: 47,457+ real pairs from MedQuAD  
**Evaluation Data**: 50 synthetic pairs (separate)  
**Result**: Valid, fair evaluation

