"""
Script to download and prepare larger medical QA datasets for evaluation.

This script downloads medical QA datasets from HuggingFace and formats them
for use in RAGAS evaluation.
"""

import json
from datasets import load_dataset
from pathlib import Path

def download_medqa_dataset():
    """Download MedQA dataset from HuggingFace."""
    try:
        # Try to load MedQA dataset
        dataset = load_dataset("bigbio/med_qa", "med_qa_en_4options", split="train")
        print(f"Loaded MedQA dataset with {len(dataset)} examples")
        
        qa_pairs = []
        for item in dataset:
            question = item.get('question', '')
            # Get the correct answer
            correct_answer_idx = item.get('answer_idx', 0)
            options = item.get('options', [])
            if options and correct_answer_idx < len(options):
                ground_truth = options[correct_answer_idx]
            else:
                ground_truth = item.get('answer', '')
            
            # Include reasoning if available
            if 'rationale' in item:
                ground_truth += f" {item['rationale']}"
            
            qa_pairs.append({
                "question": question,
                "ground_truth": ground_truth
            })
        
        return qa_pairs
    except Exception as e:
        print(f"Error loading MedQA: {e}")
        return None

def download_pubmedqa_dataset():
    """Download PubMedQA dataset from HuggingFace."""
    try:
        dataset = load_dataset("pubmed_qa", "pqa_labeled", split="train")
        print(f"Loaded PubMedQA dataset with {len(dataset)} examples")
        
        qa_pairs = []
        for item in dataset[:5000]:  # Limit to first 5000 for manageability
            question = item.get('question', '')
            long_answer = item.get('long_answer', '')
            final_decision = item.get('final_decision', '')
            
            ground_truth = long_answer if long_answer else final_decision
            if final_decision and long_answer:
                ground_truth = f"{long_answer} (Decision: {final_decision})"
            
            qa_pairs.append({
                "question": question,
                "ground_truth": ground_truth
            })
        
        return qa_pairs
    except Exception as e:
        print(f"Error loading PubMedQA: {e}")
        return None

def download_healthqa_dataset():
    """Download HealthQA dataset from HuggingFace."""
    try:
        # Try alternative health-related datasets
        dataset = load_dataset("medical_questions_pairs", split="train")
        print(f"Loaded HealthQA dataset with {len(dataset)} examples")
        
        qa_pairs = []
        for item in dataset:
            question = item.get('question', '')
            answer = item.get('answer', '')
            
            if question and answer:
                qa_pairs.append({
                    "question": question,
                    "ground_truth": answer
                })
        
        return qa_pairs
    except Exception as e:
        print(f"Error loading HealthQA: {e}")
        return None

def create_expanded_qa_dataset():
    """Create an expanded QA dataset by combining multiple sources."""
    output_path = Path(__file__).parent.parent / "docs" / "evaluation" / "qa_dataset_expanded.json"
    
    all_pairs = []
    
    # Try downloading from various sources
    print("Attempting to download MedQA...")
    medqa_pairs = download_medqa_dataset()
    if medqa_pairs:
        all_pairs.extend(medqa_pairs[:2000])  # Limit to 2000
        print(f"Added {len(medqa_pairs[:2000])} pairs from MedQA")
    
    print("Attempting to download PubMedQA...")
    pubmedqa_pairs = download_pubmedqa_dataset()
    if pubmedqa_pairs:
        all_pairs.extend(pubmedqa_pairs)
        print(f"Added {len(pubmedqa_pairs)} pairs from PubMedQA")
    
    print("Attempting to download HealthQA...")
    healthqa_pairs = download_healthqa_dataset()
    if healthqa_pairs:
        all_pairs.extend(healthqa_pairs[:1000])  # Limit to 1000
        print(f"Added {len(healthqa_pairs[:1000])} pairs from HealthQA")
    
    # If no datasets downloaded, create a larger synthetic dataset
    if not all_pairs:
        print("No datasets downloaded. Creating expanded synthetic dataset...")
        all_pairs = create_synthetic_expanded_dataset()
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(all_pairs, f, indent=2)
    
    print(f"\nTotal QA pairs created: {len(all_pairs)}")
    print(f"Saved to: {output_path}")
    
    return output_path

def create_synthetic_expanded_dataset():
    """Create a larger synthetic medical QA dataset."""
    # Expanded list of medical questions with more variety
    expanded_qa = [
        {"question": "What are the common symptoms of diabetes mellitus?", "ground_truth": "Common symptoms of diabetes mellitus include frequent urination, excessive thirst, increased hunger, unexplained weight loss, fatigue, slow-healing sores, frequent infections, blurred vision, and tingling or numbness in hands or feet."},
        {"question": "How is hypertension typically treated?", "ground_truth": "Hypertension is typically treated through lifestyle modifications including diet changes (DASH diet), regular exercise, weight loss, and limiting alcohol and salt intake. Medications such as ACE inhibitors, ARBs, beta-blockers, diuretics, or calcium channel blockers may be prescribed depending on the severity and patient factors."},
        {"question": "What are the main risk factors for coronary heart disease?", "ground_truth": "Main risk factors for coronary heart disease include high blood pressure, high cholesterol, smoking, diabetes, obesity, physical inactivity, unhealthy diet, excessive alcohol consumption, stress, and family history of heart disease."},
        {"question": "How does aspirin work to prevent blood clots?", "ground_truth": "Aspirin works by inhibiting cyclooxygenase (COX) enzymes, which reduces the production of thromboxane A2. Thromboxane A2 promotes platelet aggregation and vasoconstriction. By blocking its synthesis, aspirin prevents platelets from clumping together and forming blood clots."},
        {"question": "What are the typical treatments for community-acquired pneumonia?", "ground_truth": "Community-acquired pneumonia is typically treated with antibiotics such as amoxicillin, azithromycin, or levofloxacin, depending on the suspected pathogen and patient allergies. Supportive care includes rest, hydration, fever reducers, and oxygen therapy if needed. Hospitalization may be required for severe cases."},
        {"question": "What causes migraine headaches?", "ground_truth": "The exact cause of migraines is unknown, but they are believed to involve a combination of genetic and environmental factors. Triggers can include stress, certain foods, hormonal changes, lack of sleep, bright lights, and weather changes. The condition involves abnormal brain activity affecting nerve signals, chemicals, and blood vessels."},
        {"question": "How is asthma diagnosed?", "ground_truth": "Asthma is diagnosed through a combination of medical history, physical examination, and lung function tests. Spirometry measures how much air you can exhale and how quickly. Peak flow monitoring tracks breathing patterns. Allergy testing may identify triggers. Bronchoprovocation tests can confirm airway hyperresponsiveness."},
        {"question": "What are the stages of chronic kidney disease?", "ground_truth": "Chronic kidney disease has five stages based on glomerular filtration rate (GFR): Stage 1 (GFR ≥90, kidney damage with normal function), Stage 2 (GFR 60-89, mild damage), Stage 3 (GFR 30-59, moderate damage), Stage 4 (GFR 15-29, severe damage), Stage 5 (GFR <15, kidney failure requiring dialysis or transplant)."},
        {"question": "How does vaccination work against infectious diseases?", "ground_truth": "Vaccines work by stimulating the immune system to recognize and fight specific pathogens without causing disease. They contain weakened, inactivated, or parts of the pathogen, or genetic material that instructs cells to produce harmless pathogen components. This 'teaches' the immune system to produce antibodies and memory cells for future protection."},
        {"question": "What are the symptoms of depression?", "ground_truth": "Symptoms of depression include persistent sadness, loss of interest in activities, changes in appetite or weight, sleep disturbances, fatigue, feelings of worthlessness, difficulty concentrating, irritability, and thoughts of death or suicide. Symptoms must persist for at least two weeks for a diagnosis."},
        {"question": "How is type 2 diabetes managed?", "ground_truth": "Type 2 diabetes management includes lifestyle changes (healthy diet, regular exercise, weight loss), oral medications (metformin, sulfonylureas, DPP-4 inhibitors), injectable medications (GLP-1 agonists, insulin), blood glucose monitoring, and regular medical check-ups to prevent complications."},
        {"question": "What causes peptic ulcers?", "ground_truth": "Peptic ulcers are primarily caused by Helicobacter pylori (H. pylori) bacterial infection or long-term use of nonsteroidal anti-inflammatory drugs (NSAIDs). Other factors include smoking, excessive alcohol consumption, stress, and certain medications. H. pylori damages the protective mucus layer, allowing stomach acid to erode the lining."},
        {"question": "How is influenza diagnosed and treated?", "ground_truth": "Influenza is diagnosed through symptoms, rapid antigen tests, PCR tests, or viral culture. Treatment focuses on symptom relief with rest, fluids, and over-the-counter medications. Antiviral medications like oseltamivir (Tamiflu) can shorten duration if taken early. Annual vaccination is the best prevention."},
        {"question": "What are the complications of untreated high blood pressure?", "ground_truth": "Untreated high blood pressure can lead to heart attack, stroke, heart failure, kidney damage, vision loss, peripheral artery disease, aortic aneurysms, and cognitive decline. It damages blood vessel walls, increasing atherosclerosis risk."},
        {"question": "How does chemotherapy work in cancer treatment?", "ground_truth": "Chemotherapy uses drugs to kill rapidly dividing cancer cells. Since cancer cells divide faster than normal cells, they are more susceptible. However, it can also damage healthy cells causing side effects. Different drugs target various cell division phases. Combination therapies improve effectiveness and reduce resistance."},
        {"question": "What is the normal range for blood pressure?", "ground_truth": "Normal blood pressure is typically defined as systolic pressure below 120 mmHg and diastolic pressure below 80 mmHg. Elevated blood pressure is 120-129/<80, Stage 1 hypertension is 130-139/80-89, Stage 2 is ≥140/≥90, and hypertensive crisis is >180/>120."},
        {"question": "How is appendicitis diagnosed?", "ground_truth": "Appendicitis is diagnosed through physical examination (McBurney's point tenderness), blood tests (elevated white blood cell count), imaging studies (CT scan, ultrasound), and clinical symptoms (right lower quadrant pain, nausea, fever). Surgical removal is the standard treatment."},
        {"question": "What are the treatment options for osteoarthritis?", "ground_truth": "Osteoarthritis treatment includes pain management (NSAIDs, acetaminophen), physical therapy, exercise, weight loss, assistive devices, corticosteroid injections, hyaluronic acid injections, and in severe cases, joint replacement surgery. Lifestyle modifications are crucial for management."},
        {"question": "How is sleep apnea diagnosed?", "ground_truth": "Sleep apnea is diagnosed through sleep studies (polysomnography) that monitor breathing, oxygen levels, heart rate, and brain activity during sleep. Home sleep tests can also be used. Symptoms include loud snoring, daytime sleepiness, and witnessed breathing pauses during sleep."},
        {"question": "What are the symptoms of rheumatoid arthritis?", "ground_truth": "Symptoms of rheumatoid arthritis include joint pain, stiffness (especially in the morning), swelling, warmth, and redness in affected joints. Other symptoms may include fatigue, fever, weight loss, and rheumatoid nodules. It typically affects joints symmetrically."},
        {"question": "How is hypothyroidism treated?", "ground_truth": "Hypothyroidism is treated with synthetic thyroid hormone replacement therapy (levothyroxine). The dose is adjusted based on TSH levels and symptoms. Regular monitoring is required. Treatment is usually lifelong and helps restore normal metabolism and energy levels."},
        {"question": "What are the risk factors for stroke?", "ground_truth": "Risk factors for stroke include high blood pressure, atrial fibrillation, diabetes, high cholesterol, smoking, obesity, physical inactivity, excessive alcohol consumption, family history, age (over 55), gender (men have higher risk), and previous stroke or TIA."},
        {"question": "How is epilepsy diagnosed?", "ground_truth": "Epilepsy is diagnosed through detailed medical history, neurological examination, EEG (electroencephalogram) to detect abnormal brain activity, brain imaging (MRI or CT), and blood tests. Diagnosis requires at least two unprovoked seizures occurring more than 24 hours apart."},
        {"question": "What are the causes of anemia?", "ground_truth": "Anemia can be caused by iron deficiency, vitamin B12 or folate deficiency, blood loss, chronic diseases, bone marrow problems, hemolytic conditions, genetic disorders (sickle cell, thalassemia), and certain medications. Iron deficiency is the most common cause worldwide."},
        {"question": "How is psoriasis treated?", "ground_truth": "Psoriasis treatment includes topical medications (corticosteroids, vitamin D analogs), phototherapy (UV light), systemic medications (methotrexate, cyclosporine), biologic drugs (TNF inhibitors, IL-17 inhibitors), and lifestyle modifications. Treatment choice depends on severity and patient factors."},
        {"question": "What are the symptoms of hypothyroidism?", "ground_truth": "Symptoms of hypothyroidism include fatigue, weight gain, cold intolerance, constipation, dry skin, hair loss, muscle weakness, joint pain, depression, memory problems, slowed heart rate, and enlarged thyroid (goiter). Symptoms develop gradually and can be subtle."},
        {"question": "How is Crohn's disease managed?", "ground_truth": "Crohn's disease management includes anti-inflammatory medications (aminosalicylates, corticosteroids), immune system suppressors (azathioprine, methotrexate), biologics (TNF inhibitors), antibiotics, antidiarrheal medications, pain relievers, dietary modifications, and surgery in severe cases. Goal is to achieve and maintain remission."},
        {"question": "What are the warning signs of cancer?", "ground_truth": "Warning signs of cancer include unexplained weight loss, persistent fatigue, unusual bleeding or discharge, changes in bowel or bladder habits, persistent cough or hoarseness, difficulty swallowing, changes in moles or skin lesions, unexplained lumps, and persistent indigestion or difficulty swallowing."},
        {"question": "How is hepatitis B transmitted?", "ground_truth": "Hepatitis B is transmitted through contact with infected blood, semen, vaginal fluids, or other body fluids. Common routes include unprotected sex, sharing needles, mother-to-child during birth, and contact with open wounds. It is not spread through casual contact, food, or water."},
        {"question": "What are the treatment options for fibromyalgia?", "ground_truth": "Fibromyalgia treatment includes pain medications (pregabalin, duloxetine, milnacipran), antidepressants, sleep aids, physical therapy, exercise, stress management, cognitive behavioral therapy, and complementary therapies (acupuncture, massage). A multidisciplinary approach is most effective."},
        {"question": "How is glaucoma diagnosed?", "ground_truth": "Glaucoma is diagnosed through comprehensive eye examination including tonometry (eye pressure measurement), ophthalmoscopy (examining optic nerve), perimetry (visual field testing), pachymetry (corneal thickness), and gonioscopy (examining drainage angle). Regular eye exams are important for early detection."},
        {"question": "What are the causes of acute kidney injury?", "ground_truth": "Acute kidney injury can be caused by decreased blood flow to kidneys (dehydration, heart failure, severe infection), direct kidney damage (medications, contrast dyes, infections, toxins), or urinary tract obstruction (kidney stones, tumors, enlarged prostate). Prompt treatment is essential."},
        {"question": "How is multiple sclerosis diagnosed?", "ground_truth": "Multiple sclerosis is diagnosed through neurological examination, MRI scans showing lesions in brain and spinal cord, cerebrospinal fluid analysis (oligoclonal bands), evoked potential tests, and ruling out other conditions. Diagnosis requires evidence of lesions in different areas and at different times."},
        {"question": "What are the symptoms of Lyme disease?", "ground_truth": "Early symptoms of Lyme disease include erythema migrans rash (bull's-eye pattern), fever, chills, fatigue, body aches, headache, neck stiffness, and swollen lymph nodes. Later symptoms can include joint pain, neurological problems, and heart rhythm issues if untreated."},
        {"question": "How is endometriosis treated?", "ground_truth": "Endometriosis treatment includes pain medications (NSAIDs), hormonal therapies (birth control pills, GnRH agonists, progestin), and surgery (laparoscopy to remove endometrial tissue). In severe cases, hysterectomy may be considered. Treatment goals are pain relief and fertility preservation."},
        {"question": "What are the complications of diabetes?", "ground_truth": "Diabetes complications include cardiovascular disease, nerve damage (neuropathy), kidney damage (nephropathy), eye damage (retinopathy), foot damage, skin conditions, hearing impairment, Alzheimer's disease, and depression. Tight blood sugar control helps prevent or delay complications."},
        {"question": "How is tuberculosis diagnosed?", "ground_truth": "Tuberculosis is diagnosed through skin test (Mantoux test), blood tests (interferon-gamma release assays), chest X-ray, sputum tests (microscopy, culture, PCR), and biopsy if needed. Active TB diagnosis requires identification of Mycobacterium tuberculosis bacteria."},
        {"question": "What are the symptoms of GERD?", "ground_truth": "Symptoms of GERD (gastroesophageal reflux disease) include heartburn, regurgitation, chest pain, difficulty swallowing, sensation of lump in throat, chronic cough, hoarseness, and disrupted sleep. Symptoms worsen when lying down and may be triggered by certain foods."},
        {"question": "How is Parkinson's disease managed?", "ground_truth": "Parkinson's disease management includes medications (levodopa, dopamine agonists, MAO-B inhibitors), physical therapy, occupational therapy, speech therapy, deep brain stimulation surgery in advanced cases, and lifestyle modifications. Treatment aims to control symptoms and maintain quality of life."},
        {"question": "What are the risk factors for osteoporosis?", "ground_truth": "Risk factors for osteoporosis include age (especially postmenopausal women), gender (women at higher risk), family history, low body weight, smoking, excessive alcohol consumption, sedentary lifestyle, low calcium/vitamin D intake, certain medications (corticosteroids), and medical conditions affecting bone health."},
        {"question": "How is sepsis diagnosed and treated?", "ground_truth": "Sepsis is diagnosed through clinical signs (fever, rapid heart rate, rapid breathing), blood tests (elevated white blood cells, lactate levels), blood cultures, imaging studies, and organ function tests. Treatment requires immediate antibiotics, IV fluids, vasopressors if needed, and source control. Early recognition is critical."},
    ]
    
    return expanded_qa

if __name__ == "__main__":
    create_expanded_qa_dataset()
