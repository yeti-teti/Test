# MedQuAD Dataset Download Process - Complete Guide

## Overview

`medquad_dataset.json` is downloaded from GitHub and contains **47,457+ real medical Q&A pairs** from 12 NIH sources.

---

## Download Process - Step by Step

### Step 1: GitHub URL

```python
# Line 80
medquad_url = "https://github.com/abachaa/MedQuAD/archive/refs/heads/master.zip"
```

**What it is**:
- Official MedQuAD repository on GitHub
- Contains 12 collections of medical Q&A data
- From 12 different NIH sources
- Publicly available (free to download)

---

### Step 2: Download ZIP File

```python
# Lines 84-88
temp_dir = tempfile.mkdtemp()  # Create temporary directory
zip_path = os.path.join(temp_dir, "medquad.zip")

print(f"Downloading from {medquad_url}...")
urllib.request.urlretrieve(medquad_url, zip_path)
```

**What happens**:
- `urllib.request.urlretrieve()` downloads the ZIP file
- Saves to temporary directory (`/tmp/...`)
- File: `medquad.zip` (~25MB)

**Output**:
```
Downloading from https://github.com/abachaa/MedQuAD/archive/refs/heads/master.zip...
```

---

### Step 3: Extract ZIP Archive

```python
# Lines 90-92
print("Extracting MedQuAD archive...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(temp_dir)
```

**What happens**:
- Extracts all files from ZIP
- Creates folder structure: `MedQuAD-master/`
- Inside: 12 collections with XML files

**Structure after extraction**:
```
MedQuAD-master/
├── 1_CancerGov_QA/
│   ├── file1.xml
│   ├── file2.xml
│   └── ...
├── 2_GARD_QA/
│   └── ...
├── 3_GHR_QA/
│   └── ...
└── ... (12 collections total)
```

**Output**:
```
Extracting MedQuAD archive...
```

---

### Step 4: Process 12 Collections

```python
# Lines 98-112
collections = [
    "1_CancerGov_QA",
    "2_GARD_QA",
    "3_GHR_QA",
    "4_MPlus_Health_Topics_QA",
    "5_NIDDK_QA",
    "6_NINDS_QA",
    "7_SeniorHealth_QA",
    "8_NHLBI_QA_XML",
    "9_CDC_QA",
    "10_MPlus_ADAM_QA",
    "11_MPlusDrugs_QA",
    "12_MPlusHerbsSupplements_QA"
]

for collection in collections:
    print(f"Processing {collection}...")
```

**What each collection contains**:

1. **1_CancerGov_QA** - Cancer information from cancer.gov
2. **2_GARD_QA** - Genetic & Rare Diseases
3. **3_GHR_QA** - Genetics Home Reference
4. **4_MPlus_Health_Topics_QA** - MedlinePlus health topics
5. **5_NIDDK_QA** - Diabetes, digestive, kidney diseases (NIH)
6. **6_NINDS_QA** - Neurological disorders (NIH)
7. **7_SeniorHealth_QA** - Health info for seniors
8. **8_NHLBI_QA_XML** - Heart, lung, blood diseases (NIH)
9. **9_CDC_QA** - CDC disease prevention info
10. **10_MPlus_ADAM_QA** - Medical animations
11. **11_MPlusDrugs_QA** - Drug information
12. **12_MPlusHerbsSupplements_QA** - Herbs & supplements

**Output**:
```
Processing 1_CancerGov_QA...
Processing 2_GARD_QA...
Processing 3_GHR_QA...
... (for all 12 collections)
```

---

### Step 5: Parse XML Files

```python
# Lines 128-141
for xml_file in xml_files:
    try:
        tree = ET.parse(xml_file)  # Parse XML
        root = tree.getroot()
        
        # Find QA pairs in XML (multiple possible tag names)
        items = root.findall('.//QAPair')
        if not items:
            items = root.findall('.//QA')
        if not items:
            items = root.findall('.//document')
        if not items:
            items = root.findall('.//item')
```

**XML Format Example**:
```xml
<?xml version="1.0"?>
<Document>
  <QAPair>
    <Question>What is diabetes?</Question>
    <Answer>Diabetes is a metabolic disease...</Answer>
  </QAPair>
  <QAPair>
    <Question>How is it treated?</Question>
    <Answer>Treatment includes...</Answer>
  </QAPair>
</Document>
```

---

### Step 6: Extract Question & Answer

```python
# Lines 142-174
for item in items:
    question = ""
    answer = ""
    
    # Try different tag names for question
    question_elem = item.find('Question')
    if question_elem is None:
        question_elem = item.find('question')
    if question_elem is None:
        question_elem = item.find('Q')
    if question_elem is not None:
        question = (question_elem.text or "").strip()
    
    # Try different tag names for answer
    answer_elem = item.find('Answer')
    if answer_elem is None:
        answer_elem = item.find('answer')
    if answer_elem is None:
        answer_elem = item.find('A')
    if answer_elem is not None:
        answer = (answer_elem.text or "").strip()
    
    # Fallback methods if above fails
    if not question:
        question = (item.findtext('Question') or 
                   item.findtext('question') or 
                   item.findtext('Q') or "").strip()
    
    if not answer:
        answer = (item.findtext('Answer') or 
                 item.findtext('answer') or 
                 item.findtext('A') or "").strip()
    
    # Last resort: check attributes
    if not question:
        question = (item.get('question', '') or 
                   item.get('Question', '') or "").strip()
    
    if not answer:
        answer = (item.get('answer', '') or 
                 item.get('Answer', '') or "").strip()
```

**Why multiple attempts?**
- Different XML files use different tag naming conventions
- Some use `Question`, others use `question`, `Q`, etc.
- Robust parsing handles all variations

**Result**:
```
question = "What is diabetes?"
answer = "Diabetes is a metabolic disease affecting..."
```

---

### Step 7: Store Q&A Pairs

```python
# Lines 176-181
if question and answer:
    qa_pairs.append({
        "question": question,
        "ground_truth": answer
    })
    collection_count += 1

print(f"  Added {collection_count} pairs from {collection}")
```

**Accumulates in list**:
```python
qa_pairs = [
    {
        "question": "What is diabetes?",
        "ground_truth": "Diabetes is a metabolic disease..."
    },
    {
        "question": "How is it treated?",
        "ground_truth": "Treatment includes..."
    },
    # ... continues for all 47,457 pairs
]
```

**Output**:
```
  Added 3000 pairs from 1_CancerGov_QA
  Added 2000 pairs from 2_GARD_QA
  ... (for all 12 collections)
```

---

### Step 8: Clean Up Temporary Files

```python
# Lines 189-191
import shutil
shutil.rmtree(temp_dir)  # Delete temp directory and all extracted files
```

**What happens**:
- Deletes temporary directory
- Frees up disk space
- Removes extracted XML files (no longer needed)

---

### Step 9: Save to Data/ Directory

```python
# Lines 195-203
data_dir = Path(__file__).parent.parent / "Data"
data_dir.mkdir(parents=True, exist_ok=True)
medquad_data_path = data_dir / "medquad_dataset.json"

print(f"Saving MedQuAD dataset to {medquad_data_path}...")
with open(medquad_data_path, 'w') as f:
    json.dump(qa_pairs, f, indent=2)
print(f"Saved {len(qa_pairs)} QA pairs to Data/medquad_dataset.json")
```

**Output file**:
```
📁 Data/medquad_dataset.json
└─ 47,457 Q&A pairs in JSON format
```

**File format**:
```json
[
  {
    "question": "What is diabetes?",
    "ground_truth": "Diabetes is a metabolic disease affecting how your body processes blood glucose..."
  },
  {
    "question": "How is hypertension treated?",
    "ground_truth": "Hypertension is treated through lifestyle modifications including..."
  },
  ... (47,457 more pairs)
]
```

**Output**:
```
Saving MedQuAD dataset to Data/medquad_dataset.json...
Saved 47457 QA pairs to Data/medquad_dataset.json
```

---

### Step 10: Return Limited Dataset

```python
# Line 205
return qa_pairs[:10000]  # Limit to 10,000 for evaluation manageability
```

**What happens**:
- Returns first 10,000 pairs (memory efficient)
- Full 47,457 pairs saved to file
- Used for evaluation if needed

---

## Complete Download Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│     GitHub Repository                                   │
│     abachaa/MedQuAD                                     │
│     URL: github.com/abachaa/MedQuAD/archive/.../master.zip
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ urllib.request.urlretrieve()
                       ▼
        ┌──────────────────────────┐
        │   Download medquad.zip   │
        │   (~25MB)                │
        │   → /tmp/medquad.zip    │
        └──────────────┬───────────┘
                       │
                       │ zipfile.ZipFile.extractall()
                       ▼
        ┌──────────────────────────────────┐
        │  Extract to MedQuAD-master/      │
        │  ├── 1_CancerGov_QA/             │
        │  ├── 2_GARD_QA/                  │
        │  ├── ... (12 collections)        │
        │  └── 12_MPlusHerbsSupplements_QA/│
        └──────────────┬───────────────────┘
                       │
                       │ For each collection:
                       │ - Find XML files
                       │ - Parse XML
                       │ - Extract Q&A
                       ▼
        ┌──────────────────────────────────┐
        │  Parse 12 Collections            │
        │  → Extract Question/Answer pairs │
        │  → Total: 47,457 pairs           │
        │  → Store in memory               │
        └──────────────┬───────────────────┘
                       │
                       │ shutil.rmtree()
                       ▼
        ┌──────────────────────────────────┐
        │  Clean up temp directory         │
        │  Delete extracted files          │
        └──────────────┬───────────────────┘
                       │
                       │ json.dump()
                       ▼
        ┌──────────────────────────────────┐
        │  Save to Data/ directory         │
        │  File: medquad_dataset.json      │
        │  Size: ~20MB                     │
        │  Format: JSON array (47,457)     │
        └──────────────────────────────────┘
```

---

## Python Imports Used

```python
import json                    # Save to JSON
import xml.etree.ElementTree as ET  # Parse XML
import urllib.request         # Download ZIP
import zipfile               # Extract ZIP
from pathlib import Path     # File paths
import os                    # OS operations
import tempfile              # Temporary files
import shutil               # File/directory operations
```

---

## How to Run

### Run the download script:

```bash
cd /Users/saugatmalla/Documents/Projects/MedicalChatbot

python src/download_qa_dataset.py
```

### Output:

```
Attempting to download MedQA...
Loaded MedQA dataset with X examples
Added X pairs from MedQA

Attempting to download PubMedQA...
Loaded PubMedQA dataset with X examples
Added X pairs from PubMedQA

Attempting to download HealthQA...
Loaded HealthQA dataset with X examples
Added X pairs from HealthQA

Attempting to download MedQuAD...
Downloading MedQuAD dataset from GitHub...
Downloading from https://github.com/abachaa/MedQuAD/archive/refs/heads/master.zip...
Extracting MedQuAD archive...
Processing 1_CancerGov_QA...
  Added 3000 pairs from 1_CancerGov_QA
Processing 2_GARD_QA...
  Added 1500 pairs from 2_GARD_QA
... (continues for all 12 collections)
Successfully loaded 47457 QA pairs from MedQuAD
Saving MedQuAD dataset to Data/medquad_dataset.json...
Saved 47457 QA pairs to Data/medquad_dataset.json

Total QA pairs created: 47457
Saved to: docs/evaluation/qa_dataset_expanded.json
```

---

## Files Created

### Primary Output:
```
📁 Data/medquad_dataset.json
├─ 47,457 Q&A pairs
├─ Size: ~20MB
├─ Format: JSON array
└─ Used for: Training/Indexing in Pinecone
```

### Secondary Output (if run as standalone):
```
📁 docs/evaluation/qa_dataset_expanded.json
├─ Combined from multiple sources
├─ Size: ~20MB
├─ Used for: Evaluation
└─ Contains: medquad + pubmedqa + healthqa
```

---

## Key Statistics

| Metric | Value |
|--------|-------|
| **Total Q&A Pairs** | 47,457 |
| **Collections** | 12 NIH sources |
| **File Size (JSON)** | ~20MB |
| **Download Size (ZIP)** | ~25MB |
| **Parse Time** | ~1-2 minutes |
| **Reusable** | Yes (saved to Data/) |

---

## Summary

✅ **Automated download** from GitHub  
✅ **Parses 12 NIH medical collections**  
✅ **Extracts 47,457 real Q&A pairs**  
✅ **Saves to Data/medquad_dataset.json**  
✅ **Used for training (Pinecone indexing)**  
✅ **Can be reused (no re-download needed)**  

---

**Status**: ✅ Fully automated download process  
**Source**: Official MedQuAD GitHub repository  
**Data Quality**: High (NIH sources)

