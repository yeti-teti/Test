# Source Attribution - Real Examples

## Example 1: Disease Query (All Sources)

### User Input
```
What is type 2 diabetes?
```

### Bot Response (In Chat)

```
Type 2 diabetes is a chronic condition characterized by insulin 
resistance, where the body cannot effectively use insulin to regulate 
blood sugar levels. This leads to elevated glucose in the bloodstream. 
Risk factors include obesity, sedentary lifestyle, family history, and 
age. Management typically involves lifestyle modifications, medications 
like metformin, and regular blood glucose monitoring.

---
Sources Used:
📚 RAG Sources: medquad_dataset.json
📊 MCP (Local Data): medical_conditions.json
🌐 Web Search: mayoclinic.org, webmd.com

┌─────────────────────────────────────────────────────────┐
│ 📊 Source Breakdown:                                    │
│                                                         │
│ 📚 RAG: 2    📊 MCP: 1    🌐 Web: 2                  │
│                                                         │
│ 📚 RAG Sources: medquad_dataset.json, GALE_ENCYCLOPEDIA.pdf
│ 📊 MCP (Local): medical_conditions.json                │
│ 🌐 Web Search: mayoclinic.org, webmd.com               │
└─────────────────────────────────────────────────────────┘
```

### API Response (JSON)
```json
{
  "answer": "Type 2 diabetes is a chronic condition...\n\n---\nSources Used:\n📚 **RAG Sources**: medquad_dataset.json\n📊 **MCP (Local Data)**: medical_conditions.json\n🌐 **Web Search**: mayoclinic.org, webmd.com",
  "sources": [
    {
      "filename": "medquad_dataset.json",
      "type": "json",
      "path": "Data/medquad_dataset.json",
      "category": "RAG"
    },
    {
      "filename": "The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf",
      "type": "pdf",
      "path": "Data/The_GALE_ENCYCLOPEDIA_of_MEDICINE_SECOND.pdf",
      "category": "RAG"
    },
    {
      "filename": "medical_conditions.json",
      "type": "mcp",
      "path": "Data/medical_conditions.json",
      "relevance": 0.95,
      "category": "MCP"
    },
    {
      "filename": "Type 2 Diabetes - Mayo Clinic",
      "type": "web",
      "url": "https://www.mayoclinic.org/diseases-conditions/type-2-diabetes/symptoms-causes/syc-20351193",
      "source": "mayoclinic.org",
      "summary": "Type 2 diabetes is a long-term medical condition...",
      "category": "Web"
    },
    {
      "filename": "Diabetes Type 2 - WebMD",
      "type": "web",
      "url": "https://www.webmd.com/diabetes/type-2-diabetes",
      "source": "webmd.com",
      "summary": "Type 2 is the most common form of diabetes...",
      "category": "Web"
    }
  ],
  "source_breakdown": {
    "rag_count": 2,
    "mcp_count": 1,
    "web_count": 2,
    "total": 5
  }
}
```

---

## Example 2: Specific Drug Question (RAG + Web)

### User Input
```
What is metformin and how does it work?
```

### Bot Response (In Chat)

```
Metformin is an oral medication used to treat type 2 diabetes. It works 
primarily by:

1. Decreasing glucose production in the liver
2. Improving insulin sensitivity in muscle cells
3. Slowing carbohydrate digestion in the intestines

Common side effects include gastrointestinal disturbances, and it's 
contraindicated in patients with severe kidney disease. It's often the 
first-line medication for type 2 diabetes management.

---
Sources Used:
📚 RAG Sources: medquad_dataset.json
🌐 Web Search: webmd.com, mayoclinic.org

┌─────────────────────────────────────────────────────────┐
│ 📊 Source Breakdown:                                    │
│                                                         │
│ 📚 RAG: 1    📊 MCP: 0    🌐 Web: 2                  │
│                                                         │
│ 📚 RAG Sources: medquad_dataset.json                  │
│ 🌐 Web Search: webmd.com, mayoclinic.org              │
└─────────────────────────────────────────────────────────┘
```

### API Response (Abbreviated)
```json
{
  "source_breakdown": {
    "rag_count": 1,
    "mcp_count": 0,
    "web_count": 2,
    "total": 3
  },
  "sources": [
    {"filename": "medquad_dataset.json", "category": "RAG"},
    {"filename": "Metformin - WebMD", "category": "Web", "source": "webmd.com"},
    {"filename": "Metformin - Mayo Clinic", "category": "Web", "source": "mayoclinic.org"}
  ]
}
```

**Note**: No MCP source because no ingested dataset has metformin info.

---

## Example 3: Rare Disease (RAG + Web only)

### User Input
```
What is Ehlers-Danlos Syndrome?
```

### Bot Response (In Chat)

```
Ehlers-Danlos Syndrome (EDS) is a group of genetic connective tissue 
disorders characterized by defects in collagen synthesis or structure. 
Clinical features include:

- Skin hyperextensibility and fragility
- Joint hypermobility and instability
- Easy bruising and bleeding
- Vascular fragility in severe forms

The condition follows various inheritance patterns depending on the 
type. There is no cure, but management focuses on symptom control and 
prevention of complications.

---
Sources Used:
📚 RAG Sources: GALE_ENCYCLOPEDIA.pdf
🌐 Web Search: mayoclinic.org

┌─────────────────────────────────────────────────────────┐
│ 📊 Source Breakdown:                                    │
│                                                         │
│ 📚 RAG: 1    📊 MCP: 0    🌐 Web: 1                  │
│                                                         │
│ 📚 RAG Sources: The_GALE_ENCYCLOPEDIA_of_MEDICINE.pdf │
│ 🌐 Web Search: mayoclinic.org                          │
└─────────────────────────────────────────────────────────┘
```

**Analysis**:
- RAG found info in indexed encyclopedia
- Web found current info on Mayo Clinic
- MCP empty (no ingested dataset covers this rare disease)

---

## Example 4: Non-Medical Question (Rejected)

### User Input
```
What is the capital of France?
```

### Bot Response (In Chat)

```
Sorry, I can only answer medical-related questions.

┌─────────────────────────────────────────────────────────┐
│ ⚠️  This is not a medical query                        │
│                                                         │
│ Please ask about diseases, symptoms, medications,      │
│ treatments, health conditions, etc.                    │
└─────────────────────────────────────────────────────────┘
```

### API Response
```json
{
  "answer": "Sorry, I can only answer medical-related questions.",
  "sources": [],
  "source_breakdown": {
    "rag_count": 0,
    "mcp_count": 0,
    "web_count": 0,
    "total": 0
  }
}
```

---

## Example 5: Symptom Question (All Sources)

### User Input
```
What causes chest pain?
```

### Bot Response (In Chat)

```
Chest pain can have multiple etiologies, ranging from benign to 
life-threatening:

1. Cardiac causes: Myocardial infarction, angina, pericarditis
2. Pulmonary causes: Pneumothorax, pulmonary embolism, pneumonia
3. GI causes: GERD, esophageal spasm, peptic ulcer disease
4. Musculoskeletal causes: Muscle strain, costochondritis
5. Other: Anxiety, shingles

Severity depends on the underlying cause. Any persistent or severe 
chest pain requires immediate medical evaluation.

---
Sources Used:
📚 RAG Sources: medquad_dataset.json, GALE_ENCYCLOPEDIA.pdf
📊 MCP (Local Data): medical_conditions.json
🌐 Web Search: mayoclinic.org, nhs.uk, healthline.com

┌─────────────────────────────────────────────────────────┐
│ 📊 Source Breakdown:                                    │
│                                                         │
│ 📚 RAG: 2    📊 MCP: 1    🌐 Web: 3                  │
│                                                         │
│ 📚 RAG Sources: medquad_dataset.json, GALE_ENCYCLOPEDIA.pdf
│ 📊 MCP (Local): medical_conditions.json                │
│ 🌐 Web Search: mayoclinic.org, nhs.uk, healthline.com │
└─────────────────────────────────────────────────────────┘
```

### Key Points
- All three source types present
- Web has most results (active medical info)
- RAG and MCP provide local knowledge
- Very comprehensive answer

---

## Example 6: Current Medical Topic (Web Heavy)

### User Input
```
Latest COVID-19 variants and vaccines
```

### Bot Response (In Chat)

```
As of current information, the dominant COVID-19 variants include:

OMICRON Subvariants (XEC, KP.2, JN.1):
- Increased transmissibility
- Slightly reduced vaccine effectiveness
- Generally milder illness

RECOMMENDED VACCINES:
- 2024-2025 Updated mRNA vaccines specifically target recent variants
- CDC recommends annual COVID-19 vaccination
- High-risk individuals may need additional doses

EFFECTIVENESS:
- Current vaccines 60-70% effective against infection
- 90%+ effective against severe disease and death

This information is updated regularly as new variants emerge.

---
Sources Used:
🌐 Web Search: cdc.gov, who.int, healthline.com

┌─────────────────────────────────────────────────────────┐
│ 📊 Source Breakdown:                                    │
│                                                         │
│ 📚 RAG: 0    📊 MCP: 0    🌐 Web: 3                  │
│                                                         │
│ 🌐 Web Search: cdc.gov, who.int, healthline.com       │
└─────────────────────────────────────────────────────────┘
```

### Analysis
- **Why only Web?** 
  - Indexed documents may be outdated
  - Current info only available on web
  - Ingested datasets don't cover latest variants
  - Web search provides real-time CDC/WHO info
  
- **Best practice**: Trust web for current events

---

## Example 7: Treatment Protocol (RAG Heavy)

### User Input
```
What is the treatment protocol for hypertension?
```

### Bot Response (In Chat)

```
Hypertension treatment typically follows a stepped approach:

LIFESTYLE MODIFICATIONS (First line):
- DASH diet (Dietary Approaches to Stop Hypertension)
- Reduce sodium intake
- Regular aerobic exercise (150 min/week)
- Weight loss if overweight
- Limit alcohol

PHARMACOLOGICAL TREATMENT (If lifestyle fails):
- ACE inhibitors (e.g., lisinopril)
- ARBs (e.g., losartan)
- Calcium channel blockers (e.g., amlodipine)
- Thiazide diuretics
- Beta-blockers (second-line)

TARGET BP:
- General population: <130/80 mmHg
- Diabetes/kidney disease: <130/80 mmHg
- Older adults (>65): <130/80 mmHg (some exceptions)

---
Sources Used:
📚 RAG Sources: GALE_ENCYCLOPEDIA.pdf, medquad_dataset.json
📊 MCP (Local Data): medical_conditions.json

┌─────────────────────────────────────────────────────────┐
│ 📊 Source Breakdown:                                    │
│                                                         │
│ 📚 RAG: 2    📊 MCP: 1    🌐 Web: 0                  │
│                                                         │
│ 📚 RAG Sources: GALE_ENCYCLOPEDIA.pdf, medquad_dataset.json
│ 📊 MCP (Local): medical_conditions.json                │
└─────────────────────────────────────────────────────────┘
```

### Analysis
- **Why no Web?** Established protocols rarely change
- **Why heavy RAG?** Well-documented in indexed sources
- **MCP adds**: Structured condition data

---

## Visual Comparison Table

| Scenario | RAG | MCP | Web | Best For |
|----------|-----|-----|-----|----------|
| Common disease | ✅ | ✅ | ✅ | All sources combined |
| Established treatment | ✅ | ✅ | ⚠️ | Local knowledge |
| Current guidelines | ⚠️ | ❌ | ✅ | Web search |
| Rare disease | ✅ | ❌ | ✅ | Research sources |
| Latest research | ⚠️ | ❌ | ✅ | Real-time web |
| Structured lookup | ✅ | ✅ | ❌ | Local data |

---

## How Users Can Interpret Sources

### Heavy RAG (📚 majority)
**Meaning**: Well-established medical knowledge in indexes
**Trust**: High - thoroughly indexed content
**Age**: Usually good, core knowledge

### Heavy MCP (📊 majority)
**Meaning**: Exact match in ingested datasets
**Trust**: High - structured, verified data
**Age**: Depends on dataset currency

### Heavy Web (🌐 majority)
**Meaning**: Current real-time information
**Trust**: High - authoritative medical sites
**Age**: Latest (today/this week)

### Balanced (Mix)
**Meaning**: Multiple authoritative sources agree
**Trust**: Very High - strongest confidence
**Age**: Mix of perspectives

### Only One Type
**Possible Issues**:
- Limited knowledge base
- Topic not covered in other sources
- Search may need refinement

---

## Summary

The source attribution shows:

1. **What was searched** (RAG/MCP/Web)
2. **How many sources** (count per type)
3. **Where answers came from** (specific files/domains)
4. **Search effectiveness** (which methods found info)
5. **Answer confidence** (more sources = higher confidence)

**More diverse sources = Better answers! ✨**

---

**Next Steps**:
- Ask medical questions normally
- Look for the Source Breakdown box
- Verify sources match topic
- Report if a source seems wrong


