# Medical Chatbot - Test Questions

**How to Use This**:

1. Start the app: `python app.py`
2. Open browser: `http://localhost:8080`
3. Type each question below
4. Compare with expected result

---

## ✅ Medical Questions (Should Work)

### Test 1: Common Disease

**Question**:

```
What are the symptoms of diabetes?
```

**Expected Result**:

- ✅ Bot returns symptoms of diabetes
- ✅ Includes: frequent urination, thirst, hunger, weight loss, fatigue
- ✅ Shows source citations like `[Source: medical_conditions.json]`

**Example Answer**:

```
Common symptoms of diabetes mellitus include frequent urination (polyuria), 
excessive thirst (polydipsia), increased hunger, unexplained weight loss, 
fatigue, slow-healing sores, and blurred vision.

[Source: The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf]
```

---

### Test 2: Medical Treatment

**Question**:

```
How is hypertension treated?
```

**Expected Result**:

- ✅ Bot returns treatment methods
- ✅ Mentions: lifestyle changes, diet, exercise, medications
- ✅ Shows sources

**Example Answer**:

```
Hypertension is typically treated through lifestyle modifications including 
diet changes (DASH diet), regular exercise, weight loss, and limiting alcohol 
and salt intake. Medications such as ACE inhibitors, beta-blockers, or 
diuretics may be prescribed depending on severity.

[Source: medical_conditions.json]
```

---

### Test 3: Medical Condition

**Question**:

```
What causes pneumonia?
```

**Expected Result**:

- ✅ Bot explains causes
- ✅ Mentions: bacteria, viruses, fungi
- ✅ Shows sources

---

### Test 4: Drug/Medication

**Question**:

```
What is aspirin used for?
```

**Expected Result**:

- ✅ Bot explains aspirin uses
- ✅ Mentions: pain relief, blood clots, heart attacks
- ✅ Shows sources

---

### Test 5: Symptoms

**Question**:

```
What are the signs of a heart attack?
```

**Expected Result**:

- ✅ Bot lists heart attack symptoms
- ✅ Mentions: chest pain, shortness of breath, sweating, nausea
- ✅ Shows sources

---

### Test 6: Medical Procedure

**Question**:

```
What is CPR and how is it performed?
```

**Expected Result**:

- ✅ Bot explains CPR
- ✅ Mentions: chest compressions, breathing
- ✅ Shows sources

---

### Test 7: Disease Risk Factors

**Question**:

```
What are the risk factors for stroke?
```

**Expected Result**:

- ✅ Bot lists stroke risk factors
- ✅ Mentions: high blood pressure, smoking, obesity, diabetes
- ✅ Shows sources

---

### Test 8: Medical Definition

**Question**:

```
What is anemia?
```

**Expected Result**:

- ✅ Bot defines anemia
- ✅ Mentions: low red blood cells, fatigue, weakness
- ✅ Shows sources

---

### Test 9: Treatment Method

**Question**:

```
How is asthma treated?
```

**Expected Result**:

- ✅ Bot returns asthma treatments
- ✅ Mentions: inhalers, medications, avoiding triggers
- ✅ Shows sources

---

### Test 10: Vaccination

**Question**:

```
What is the purpose of vaccinations?
```

**Expected Result**:

- ✅ Bot explains vaccines
- ✅ Mentions: prevent diseases, build immunity
- ✅ Shows sources

---

## ❌ Non-Medical Questions (Should Be Rejected)

### Test 11: Random Topic

**Question**:

```
What's the capital of France?
```

**Expected Result**:

- ✅ Bot rejects it
- ✅ Response: `"Sorry, I can only answer medical-related questions."`
- ✅ No sources shown

---

### Test 12: Technology Question

**Question**:

```
What is Python programming?
```

**Expected Result**:

- ✅ Bot rejects it
- ✅ Response: `"Sorry, I can only answer medical-related questions."`

---

### Test 13: Food Question

**Question**:

```
How do I make a pizza?
```

**Expected Result**:

- ✅ Bot rejects it
- ✅ Response: `"Sorry, I can only answer medical-related questions."`

---

### Test 14: Sports Question

**Question**:

```
Who won the World Cup?
```

**Expected Result**:

- ✅ Bot rejects it
- ✅ Response: `"Sorry, I can only answer medical-related questions."`

---

## 💬 Small Talk (Should Work Directly)

### Test 15: Greeting

**Question**:

```
Hello!
```

**Expected Result**:

- ✅ Bot responds: `"Hello! How can I help you with a medical question today?"`
- ✅ No sources shown
- ✅ Instant response (no RAG needed)

---

### Test 16: Goodbye

**Question**:

```
Goodbye
```

**Expected Result**:

- ✅ Bot responds: `"Goodbye! Stay healthy."`
- ✅ Instant response

---

### Test 17: Thanks

**Question**:

```
Thank you!
```

**Expected Result**:

- ✅ Bot responds: `"You're welcome! Do you have another medical question?"`
- ✅ Instant response

---

## 🔄 Dataset Ingestion (MCP Test)

### Test 18: List Datasets

**Question**:

```
list datasets
```

**Expected Result**:

- ✅ Bot responds with available datasets
- ✅ Shows: `📊 Found X ingested dataset(s):`
- ✅ Lists dataset names, formats, record counts

**Example**:

```
📊 Found 3 ingested dataset(s):
• medical_conditions (json, 1,524 records)
• medical_diseases (csv, 812 records)
• mimic_iv_reference (json, 5,234 records)

Note: These datasets are tracked by MCP. To make them searchable, 
run 'python store_index.py'.
```

---

### Test 19: Show Datasets

**Question**:

```
show datasets
```

**Expected Result**:

- ✅ Same as Test 18 (lists all datasets)

---

### Test 20: Ingest Dataset

**Question**:

```
ingest dataset medical_conditions.json
```

**Expected Result**:

- ✅ Bot responds with success message
- ✅ Shows dataset details: format, record count

**Example**:

```
✅ Successfully ingested dataset 'medical_conditions'!

📊 Details:
- Format: json
- Records: 1,524
- Total documents: 1,524

⚠️ Note: To make this data searchable, run 'python store_index.py'
```

---

## 📊 Quick Test Summary

| Test # | Question                               | Type        | Expected            | Result |
| ------ | -------------------------------------- | ----------- | ------------------- | ------ |
| 1      | What are the symptoms of diabetes?     | Medical     | ✅ Answer + Sources | -      |
| 2      | How is hypertension treated?           | Medical     | ✅ Answer + Sources | -      |
| 3      | What causes pneumonia?                 | Medical     | ✅ Answer + Sources | -      |
| 4      | What is aspirin used for?              | Medical     | ✅ Answer + Sources | -      |
| 5      | What are signs of heart attack?        | Medical     | ✅ Answer + Sources | -      |
| 6      | What is CPR?                           | Medical     | ✅ Answer + Sources | -      |
| 7      | What are stroke risk factors?          | Medical     | ✅ Answer + Sources | -      |
| 8      | What is anemia?                        | Medical     | ✅ Answer + Sources | -      |
| 9      | How is asthma treated?                 | Medical     | ✅ Answer + Sources | -      |
| 10     | Purpose of vaccinations?               | Medical     | ✅ Answer + Sources | -      |
| 11     | What's the capital of France?          | Non-Medical | ❌ Rejection        | -      |
| 12     | What is Python?                        | Non-Medical | ❌ Rejection        | -      |
| 13     | How to make pizza?                     | Non-Medical | ❌ Rejection        | -      |
| 14     | Who won World Cup?                     | Non-Medical | ❌ Rejection        | -      |
| 15     | Hello!                                 | Small Talk  | ✅ Greeting         | -      |
| 16     | Goodbye                                | Small Talk  | ✅ Farewell         | -      |
| 17     | Thank you!                             | Small Talk  | ✅ Thanks           | -      |
| 18     | list datasets                          | MCP         | ✅ List             | -      |
| 19     | show datasets                          | MCP         | ✅ List             | -      |
| 20     | ingest dataset medical_conditions.json | MCP         | ✅ Ingest           | -      |

---

## 🚀 How to Run Full Test

```bash
# 1. Start app
python app.py

# 2. Open browser
open http://localhost:8080

# 3. Copy-paste questions from this file one by one
# 4. Compare with expected results above
# 5. Mark each test as PASS or FAIL
```

---

## ✅ Success Criteria

**All tests pass if**:

- ✅ Medical questions return relevant answers with sources
- ✅ Non-medical questions are rejected with appropriate message
- ✅ Small talk works instantly
- ✅ Dataset commands work (list/ingest)
- ✅ No error messages
- ✅ Responses are fast (2-4 seconds)

---

**Status**: Ready to test! 🧪
