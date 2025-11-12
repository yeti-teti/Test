"""
Script to ingest MIMIC-IV dataset (Medical Information Mart for Intensive Care)

MIMIC-IV is a large, freely-available database of de-identified intensive care unit (ICU)
admissions. It contains hospital records of ICU patients including vital signs, medications,
lab tests, medical procedures, and diagnoses.

Reference:
[1] Goldberger, A. L., Amaral, L. A., Glass, L., Hausdorff, J. M., Ivanov, P. C., Mark, R. G., ... & Stanley, H. E. (2000).
PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals.
Circulation, 101(23), e215-e220.

[2] Johnson, A. E., Pollard, T. J., Shen, L., Lehman, L. W. H., Feng, M., Ghassemi, M., ... & Mark, R. G. (2016).
MIMIC-III, a freely accessible critical care database. Scientific data, 3(1), 1-9.

Note: MIMIC-IV requires authentication via PhysioNet (https://physionet.org/).
This script provides a framework for ingesting MIMIC-IV data once access is granted.
"""

import json
import csv
import gzip
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from langchain_core.documents import Document
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MIMICIVDatasetIngester:
    """Ingest and process MIMIC-IV dataset files."""
    
    def __init__(self, mimic_data_dir: str = "Data/mimic-iv"):
        """
        Initialize MIMIC-IV ingester.
        
        Args:
            mimic_data_dir: Directory containing MIMIC-IV data files
        """
        self.mimic_data_dir = Path(mimic_data_dir)
        self.output_dir = Path("Data/")
        self.processed_data = []
    
    def ingest_patients_file(self, file_path: Optional[str] = None) -> List[Document]:
        """
        Ingest MIMIC-IV patients.csv file.
        
        Contains patient demographics: subject_id, gender, anchor_age, anchor_year
        
        Args:
            file_path: Path to patients.csv (auto-detected if None)
            
        Returns:
            List of Document objects
        """
        if file_path is None:
            # Try common MIMIC-IV directory structures
            possible_paths = [
                self.mimic_data_dir / "hosp" / "patients.csv",
                self.mimic_data_dir / "patients.csv",
            ]
            file_path = next((p for p in possible_paths if p.exists()), None)
            
            if file_path is None:
                logger.warning("MIMIC-IV patients.csv not found")
                return []
        
        documents = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    content = (
                        f"Patient Demographics - Subject ID: {row.get('subject_id', 'N/A')}\n"
                        f"Gender: {row.get('gender', 'N/A')}\n"
                        f"Age (at anchor year): {row.get('anchor_age', 'N/A')}\n"
                        f"Anchor Year: {row.get('anchor_year', 'N/A')}"
                    )
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': str(file_path),
                            'type': 'mimic_patients',
                            'subject_id': row.get('subject_id'),
                            'record_type': 'patient_demographics'
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"Ingested {len(documents)} patient records from MIMIC-IV")
            return documents
            
        except Exception as e:
            logger.error(f"Error ingesting patients file: {e}")
            return []
    
    def ingest_admissions_file(self, file_path: Optional[str] = None) -> List[Document]:
        """
        Ingest MIMIC-IV admissions.csv file.
        
        Contains admission information: admission_type, admission_location, discharge_location
        insurance, language, marital_status, ethnicity, etc.
        
        Args:
            file_path: Path to admissions.csv
            
        Returns:
            List of Document objects
        """
        if file_path is None:
            possible_paths = [
                self.mimic_data_dir / "hosp" / "admissions.csv",
                self.mimic_data_dir / "admissions.csv",
            ]
            file_path = next((p for p in possible_paths if p.exists()), None)
            
            if file_path is None:
                logger.warning("MIMIC-IV admissions.csv not found")
                return []
        
        documents = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    content = (
                        f"Hospital Admission - Admission Type: {row.get('admission_type', 'N/A')}\n"
                        f"Admission Location: {row.get('admission_location', 'N/A')}\n"
                        f"Discharge Location: {row.get('discharge_location', 'N/A')}\n"
                        f"Insurance: {row.get('insurance', 'N/A')}\n"
                        f"Language: {row.get('language', 'N/A')}\n"
                        f"Marital Status: {row.get('marital_status', 'N/A')}\n"
                        f"Ethnicity: {row.get('ethnicity', 'N/A')}\n"
                        f"Admission Time: {row.get('admittime', 'N/A')}\n"
                        f"Discharge Time: {row.get('dischtime', 'N/A')}"
                    )
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': str(file_path),
                            'type': 'mimic_admission',
                            'subject_id': row.get('subject_id'),
                            'hadm_id': row.get('hadm_id'),
                            'record_type': 'hospital_admission'
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"Ingested {len(documents)} admission records from MIMIC-IV")
            return documents
            
        except Exception as e:
            logger.error(f"Error ingesting admissions file: {e}")
            return []
    
    def ingest_diagnoses_file(self, file_path: Optional[str] = None) -> List[Document]:
        """
        Ingest MIMIC-IV diagnoses_icd.csv file.
        
        Contains ICD-9 and ICD-10 diagnosis codes with descriptions.
        
        Args:
            file_path: Path to diagnoses_icd.csv
            
        Returns:
            List of Document objects
        """
        if file_path is None:
            possible_paths = [
                self.mimic_data_dir / "hosp" / "diagnoses_icd.csv",
                self.mimic_data_dir / "diagnoses_icd.csv",
            ]
            file_path = next((p for p in possible_paths if p.exists()), None)
            
            if file_path is None:
                logger.warning("MIMIC-IV diagnoses_icd.csv not found")
                return []
        
        documents = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    content = (
                        f"Diagnosis - Subject ID: {row.get('subject_id', 'N/A')}\n"
                        f"Admission ID: {row.get('hadm_id', 'N/A')}\n"
                        f"Sequence: {row.get('seq_num', 'N/A')}\n"
                        f"ICD Code: {row.get('icd_code', 'N/A')}\n"
                        f"ICD Version: {row.get('icd_version', 'N/A')}\n"
                        f"Description: {row.get('long_title', 'N/A')}"
                    )
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': str(file_path),
                            'type': 'mimic_diagnosis',
                            'subject_id': row.get('subject_id'),
                            'hadm_id': row.get('hadm_id'),
                            'icd_code': row.get('icd_code'),
                            'record_type': 'clinical_diagnosis'
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"Ingested {len(documents)} diagnosis records from MIMIC-IV")
            return documents
            
        except Exception as e:
            logger.error(f"Error ingesting diagnoses file: {e}")
            return []
    
    def ingest_d_icd_diagnoses(self, file_path: Optional[str] = None) -> List[Document]:
        """
        Ingest MIMIC-IV d_icd_diagnoses.csv file.
        
        Contains ICD diagnosis code to description mappings.
        
        Args:
            file_path: Path to d_icd_diagnoses.csv
            
        Returns:
            List of Document objects
        """
        if file_path is None:
            possible_paths = [
                self.mimic_data_dir / "hosp" / "d_icd_diagnoses.csv",
                self.mimic_data_dir / "d_icd_diagnoses.csv",
            ]
            file_path = next((p for p in possible_paths if p.exists()), None)
            
            if file_path is None:
                logger.warning("MIMIC-IV d_icd_diagnoses.csv not found")
                return []
        
        documents = []
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    content = (
                        f"ICD-{row.get('icd_version', '10')} Diagnosis Code: {row.get('icd_code', 'N/A')}\n"
                        f"Short Title: {row.get('short_title', 'N/A')}\n"
                        f"Long Title: {row.get('long_title', 'N/A')}"
                    )
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': str(file_path),
                            'type': 'mimic_icd_mapping',
                            'icd_code': row.get('icd_code'),
                            'icd_version': row.get('icd_version'),
                            'record_type': 'diagnostic_code_mapping'
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"Ingested {len(documents)} ICD diagnosis mappings from MIMIC-IV")
            return documents
            
        except Exception as e:
            logger.error(f"Error ingesting ICD diagnoses mappings: {e}")
            return []
    
    def create_mimic_summary_dataset(self) -> List[Document]:
        """
        Create a comprehensive MIMIC-IV summary dataset for medical reference.
        
        This generates documents with MIMIC-IV statistics and common conditions.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        # MIMIC-IV overview and statistics
        mimic_overview = Document(
            page_content="""
MIMIC-IV Database Overview

MIMIC-IV (Medical Information Mart for Intensive Care IV) is a large, freely available 
database of de-identified intensive care unit (ICU) admissions. The database is developed, 
maintained, and hosted by the MIT Laboratory for Computational Physiology.

Database Statistics:
- Contains data from ~380,000 unique admissions to ICUs
- Covers intensive care unit stays between 2008 and 2019
- Includes ~345,000 unique patients
- 100+ variables per admission including vital signs, medications, lab tests, and procedures

Key Data Elements:
1. Patient Demographics: age, gender, ethnicity, marital status
2. Admission Data: admission type, source, insurance, language
3. Clinical Data: vital signs, lab values, medications, procedures
4. Outcome Data: mortality, length of stay, discharge disposition

Data Quality:
- De-identified using HIPAA-compliant standards
- Covers a diverse ICU population
- Includes both medical and surgical admissions
- Comprehensive temporal data for longitudinal analysis

Clinical Applications:
- ICU risk prediction models
- Clinical decision support systems
- Benchmarking hospital performance
- Epidemiological research
- Drug safety and adverse event detection
""",
            metadata={
                'source': 'MIMIC-IV_Overview',
                'type': 'reference_documentation',
                'record_type': 'database_reference'
            }
        )
        documents.append(mimic_overview)
        
        # Common ICU diagnoses from MIMIC-IV
        common_diagnoses = Document(
            page_content="""
Common ICU Diagnoses in MIMIC-IV Database

Based on analysis of MIMIC-IV admissions, the following are among the most common diagnoses:

Cardiovascular Conditions:
- Hypertension (HTN): Blood pressure disorder affecting 40-50% of ICU admissions
- Coronary artery disease (CAD): Leading cause of ICU admission
- Acute myocardial infarction (MI): Heart attack requiring intensive monitoring
- Atrial fibrillation (AFib): Common arrhythmia in critically ill patients
- Heart failure: Reduced ejection fraction requiring intensive support

Respiratory Conditions:
- Pneumonia: Bacterial or viral infection of lungs
- COPD (Chronic obstructive pulmonary disease): Chronic lung disease
- Acute respiratory distress syndrome (ARDS): Severe lung inflammation
- Asthma exacerbation: Acute worsening of asthma

Metabolic and Renal:
- Acute kidney injury (AKI): Sudden loss of kidney function
- Chronic kidney disease (CKD): Long-term kidney dysfunction
- Diabetes mellitus: Blood sugar regulation disorder
- Sepsis: Life-threatening infection response

Neurological:
- Stroke: Cerebrovascular accident
- Seizures: Abnormal electrical brain activity
- Traumatic brain injury (TBI): Head trauma with brain damage
- Encephalopathy: Brain dysfunction from various causes

GI and Hepatic:
- Acute liver failure: Rapid loss of liver function
- Gastrointestinal bleeding: Bleeding in digestive tract
- Pancreatitis: Inflammation of pancreas
- Peritonitis: Inflammation of abdominal membrane
""",
            metadata={
                'source': 'MIMIC-IV_Common_Diagnoses',
                'type': 'reference_documentation',
                'record_type': 'clinical_reference'
            }
        )
        documents.append(common_diagnoses)
        
        # MIMIC-IV medications
        medications = Document(
            page_content="""
Common Medications in MIMIC-IV Database

MIMIC-IV contains detailed medication administration records including dosages, routes,
and timing. Common medication classes in ICU admissions include:

Cardiovascular Medications:
- Beta-blockers (metoprolol, esmolol): Heart rate and blood pressure control
- ACE inhibitors: Blood pressure and heart failure management
- Vasopressors (dopamine, norepinephrine): Blood pressure support
- Anticoagulants (heparin, warfarin): Clot prevention
- Antiplatelet agents (aspirin, clopidogrel): Thrombotic event prevention

Antibiotics:
- Beta-lactams (penicillins, cephalosporins): Bacterial infection treatment
- Fluoroquinolones: Broad-spectrum infection coverage
- Aminoglycosides: Gram-negative coverage
- Vancomycin: Methicillin-resistant Staphylococcus aureus (MRSA) coverage
- Antifungals: Fungal infection treatment

Sedation and Pain Control:
- Propofol: Anesthetic agent for sedation
- Midazolam: Benzodiazepine for sedation
- Fentanyl: Opioid analgesic for pain control
- Morphine: Opioid for pain and dyspnea relief
- Dexmedetomidine: Alpha-2 agonist for sedation

Respiratory Support:
- Albuterol: Bronchodilator for airway management
- Ipratropium: Anticholinergic bronchodilator
- Methylxanthines (theophylline): Bronchodilation
- Inhaled nitric oxide: Pulmonary vasodilator

Metabolic:
- Insulin: Blood glucose control
- Corticosteroids (dexamethasone, hydrocortisone): Inflammation reduction
- Diuretics (furosemide, spironolactone): Fluid management
""",
            metadata={
                'source': 'MIMIC-IV_Medications',
                'type': 'reference_documentation',
                'record_type': 'medication_reference'
            }
        )
        documents.append(medications)
        
        # MIMIC-IV vital signs
        vital_signs = Document(
            page_content="""
Vital Signs and Lab Values in MIMIC-IV

MIMIC-IV contains high-frequency vital signs and laboratory values for ICU patients.
These are critical for monitoring patient condition and guiding clinical decisions.

Vital Signs:
- Heart Rate (HR): 40-200 bpm; normal range 60-100 bpm at rest
- Blood Pressure (BP): Systolic and diastolic; normal <120/80 mmHg
  - Systolic (SBP): Normal <120, elevated 120-129, high ≥130
  - Diastolic (DBP): Normal <80, elevated ≥80
- Respiratory Rate (RR): 12-20 breaths/minute normal range
- Temperature: Normal 36.5-37.5°C (97.7-99.5°F)
- Oxygen Saturation (SpO2): Normal ≥95% on room air

Hemodynamic Monitoring:
- Central Venous Pressure (CVP): 2-8 mmHg normal
- Pulmonary Artery Pressure (PAP): 15-30 systolic, 5-15 diastolic
- Cardiac Output (CO): 4-8 L/min normal range
- Mixed Venous Oxygen Saturation (SvO2): ≥70% indicates adequate perfusion

Laboratory Values (Common):
- Complete Blood Count (CBC):
  - Hemoglobin (Hgb): 13.5-17.5 g/dL (male), 12.0-15.5 g/dL (female)
  - Hematocrit (Hct): 40-54% (male), 36-46% (female)
  - White Blood Cell (WBC): 4.5-11.0 × 10^9/L
  - Platelet Count: 150-400 × 10^9/L

- Comprehensive Metabolic Panel (CMP):
  - Sodium (Na+): 135-145 mEq/L
  - Potassium (K+): 3.5-5.0 mEq/L
  - Chloride (Cl-): 98-107 mEq/L
  - Carbon Dioxide (CO2): 23-29 mEq/L
  - Blood Urea Nitrogen (BUN): 7-20 mg/dL
  - Creatinine: 0.7-1.3 mg/dL
  - Glucose: 70-100 mg/dL fasting

- Liver Function Tests:
  - Aspartate Aminotransferase (AST): 10-40 IU/L
  - Alanine Aminotransferase (ALT): 7-56 IU/L
  - Total Bilirubin: 0.1-1.2 mg/dL
  - Albumin: 3.5-5.5 g/dL

- Coagulation:
  - Prothrombin Time (PT): 11-13.5 seconds
  - Partial Thromboplastin Time (PTT): 25-35 seconds
  - International Normalized Ratio (INR): 0.8-1.1

- Arterial Blood Gas (ABG):
  - pH: 7.35-7.45
  - Partial Pressure of Carbon Dioxide (PaCO2): 35-45 mmHg
  - Partial Pressure of Oxygen (PaO2): 80-100 mmHg
  - Bicarbonate (HCO3-): 22-26 mEq/L
  - Oxygen Saturation (SaO2): 95-100%
""",
            metadata={
                'source': 'MIMIC-IV_Vital_Signs',
                'type': 'reference_documentation',
                'record_type': 'vital_signs_reference'
            }
        )
        documents.append(vital_signs)
        
        return documents
    
    def ingest_all(self) -> List[Document]:
        """
        Ingest all available MIMIC-IV data files.
        
        Returns:
            Combined list of all ingested documents
        """
        all_documents = []
        
        logger.info("Starting MIMIC-IV dataset ingestion...")
        
        # Ingest summary/reference documents
        all_documents.extend(self.create_mimic_summary_dataset())
        
        # Ingest actual data files if they exist
        all_documents.extend(self.ingest_patients_file())
        all_documents.extend(self.ingest_admissions_file())
        all_documents.extend(self.ingest_diagnoses_file())
        all_documents.extend(self.ingest_d_icd_diagnoses())
        
        logger.info(f"MIMIC-IV ingestion complete. Total documents: {len(all_documents)}")
        self.processed_data = all_documents
        
        return all_documents
    
    def save_to_json(self, output_file: str = "Data/mimic_iv_reference.json") -> str:
        """
        Save ingested data as JSON for indexing.
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = []
        for doc in self.processed_data:
            data.append({
                'content': doc.page_content,
                'metadata': doc.metadata
            })
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(data)} MIMIC-IV documents to {output_path}")
        return str(output_path)


def main():
    """Main function to ingest MIMIC-IV data."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest MIMIC-IV dataset")
    parser.add_argument(
        "--mimic-dir",
        default="Data/mimic-iv",
        help="Directory containing MIMIC-IV data files"
    )
    parser.add_argument(
        "--output",
        default="Data/mimic_iv_reference.json",
        help="Output JSON file for ingested data"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only create summary/reference documents (no actual patient data)"
    )
    
    args = parser.parse_args()
    
    ingester = MIMICIVDatasetIngester(mimic_data_dir=args.mimic_dir)
    
    if args.summary_only:
        logger.info("Creating MIMIC-IV reference documents only...")
        documents = ingester.create_mimic_summary_dataset()
    else:
        documents = ingester.ingest_all()
    
    ingester.processed_data = documents
    output_path = ingester.save_to_json(args.output)
    
    print(f"\n✅ MIMIC-IV ingestion complete!")
    print(f"   Total documents: {len(documents)}")
    print(f"   Output file: {output_path}")
    print(f"\n   Next steps:")
    print(f"   1. Run: python store_index.py")
    print(f"   2. Start the chatbot: python app.py")


if __name__ == "__main__":
    main()

