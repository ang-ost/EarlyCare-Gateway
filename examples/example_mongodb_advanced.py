"""
Advanced MongoDB Usage Example with Complete Workflow

This script demonstrates the complete workflow of the EarlyCare Gateway:
1. Patient registration
2. Clinical data collection (text, signals, images)
3. Patient record creation with processing context
4. Decision support generation
5. Audit logging
6. Querying and analysis

This example shows how all the schemas work together.
"""

from datetime import datetime, timedelta
from src.models.patient import Patient, PatientRecord, Gender
from src.models.clinical_data import TextData, SignalData, ImageData, DataSource, DataType
from src.models.decision import DecisionSupport, DiagnosisResult, UrgencyLevel, ConfidenceLevel
from src.database.mongodb_repository import MongoDBPatientRepository
import random


def generate_sample_data():
    """Generate sample patient data for demonstration."""
    
    # Sample patients
    patients = [
        {
            "patient_id": "P2024001",
            "date_of_birth": datetime(1975, 3, 15),
            "gender": Gender.FEMALE,
            "medical_record_number": "MRN789456",
            "chief_complaint": "Chest pain and shortness of breath",
            "medical_history": ["Hypertension", "Type 2 Diabetes", "Hyperlipidemia"],
            "current_medications": ["Metformin 1000mg", "Lisinopril 10mg", "Atorvastatin 20mg"],
            "allergies": ["Penicillin"],
            "ethnicity": "Caucasian",
            "primary_language": "en"
        },
        {
            "patient_id": "P2024002",
            "date_of_birth": datetime(1988, 7, 22),
            "gender": Gender.MALE,
            "medical_record_number": "MRN789457",
            "chief_complaint": "Persistent cough and fever",
            "medical_history": ["Asthma"],
            "current_medications": ["Albuterol inhaler"],
            "allergies": [],
            "ethnicity": "Asian",
            "primary_language": "en"
        },
        {
            "patient_id": "P2024003",
            "date_of_birth": datetime(2022, 1, 10),
            "gender": Gender.MALE,
            "medical_record_number": "MRN789458",
            "chief_complaint": "High fever and rash",
            "medical_history": ["Premature birth"],
            "current_medications": [],
            "allergies": ["Sulfa drugs"],
            "ethnicity": "Hispanic",
            "primary_language": "es"
        }
    ]
    
    return patients


def create_clinical_data_examples(patient_id: str):
    """Create example clinical data for a patient."""
    
    # Text data - Clinical note
    text_data = TextData(
        data_id=f"TXT-{patient_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        patient_id=patient_id,
        timestamp=datetime.now(),
        source=DataSource.EHR,
        text_content="""
        ADMISSION NOTE
        
        Patient presents to ED with complaint of chest pain radiating to left arm.
        Pain started approximately 2 hours ago while at rest.
        Patient describes pain as crushing, 8/10 severity.
        Associated symptoms: diaphoresis, nausea, shortness of breath.
        
        VITAL SIGNS:
        BP: 145/92 mmHg
        HR: 98 bpm
        RR: 22 breaths/min
        Temp: 37.1°C
        SpO2: 94% on room air
        
        PHYSICAL EXAM:
        General: Appears distressed, diaphoretic
        Cardiovascular: Regular rhythm, no murmurs
        Respiratory: Mild tachypnea, clear lung sounds bilaterally
        
        ASSESSMENT: Acute coronary syndrome - rule out myocardial infarction
        PLAN: ECG, cardiac enzymes, chest X-ray, cardiology consult
        """,
        language="en",
        document_type="admission_note"
    )
    text_data.validate()
    
    # Signal data - ECG
    # Simulated ECG signal (1000 samples at 250 Hz = 4 seconds)
    ecg_values = [round(random.uniform(0.5, 1.5), 3) for _ in range(1000)]
    
    signal_data = SignalData(
        data_id=f"SIG-{patient_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        patient_id=patient_id,
        timestamp=datetime.now(),
        source=DataSource.WEARABLE,
        signal_values=ecg_values,
        sampling_rate=250.0,
        signal_type="ECG Lead II",
        units="mV",
        duration=4.0
    )
    signal_data.validate()
    
    # Image data - Chest X-ray
    image_data = ImageData(
        data_id=f"IMG-{patient_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        patient_id=patient_id,
        timestamp=datetime.now(),
        source=DataSource.IMAGING,
        image_path=f"/images/chest_xray_{patient_id}.dcm",
        image_format="DICOM",
        modality="X-Ray",
        dimensions=(1024, 1024, 1),
        body_part="Chest",
        contrast_used=False
    )
    image_data.validate()
    
    return [text_data, signal_data, image_data]


def create_processing_context(patient: Patient, clinical_data_count: int):
    """Create processing context from chain of responsibility."""
    
    return {
        "processing_context": {
            "validation": {
                "is_valid": True,
                "errors": [],
                "warnings": []
            },
            "enrichment": {
                "age_calculated": True,
                "processing_timestamp": datetime.now().isoformat(),
                "data_count": clinical_data_count,
                "average_data_quality": 0.95,
                "has_text_data": True,
                "has_signal_data": True,
                "has_image_data": True,
                "has_critical_history": len(patient.medical_history) > 0
            },
            "triage": {
                "score": 85.0,
                "priority": "urgent",
                "factors": [
                    "Base priority: urgent",
                    "Complex medical history",
                    "Critical medical history"
                ]
            },
            "privacy": {
                "pii_detected": True,
                "anonymization_required": False,
                "compliance_flags": ["Consent verified"]
            },
            "processing_times": {
                "ValidationHandler": 12.5,
                "EnrichmentHandler": 8.3,
                "TriageHandler": 5.2,
                "PrivacyCheckHandler": 3.1
            }
        }
    }


def create_decision_support_example(patient_id: str, encounter_id: str):
    """Create example decision support result."""
    
    # Create diagnosis results
    diagnosis1 = DiagnosisResult(
        condition="Acute Coronary Syndrome",
        icd_code="I24.9",
        confidence_score=0.82,
        evidence=[
            "Chest pain with radiation to left arm",
            "Elevated cardiac biomarkers",
            "ECG changes suggestive of ischemia"
        ],
        risk_factors=[
            "Hypertension",
            "Diabetes mellitus",
            "Hyperlipidemia"
        ],
        differential_diagnoses=[
            "Unstable angina",
            "STEMI",
            "NSTEMI"
        ],
        recommended_tests=[
            "Serial troponin measurements",
            "Coronary angiography",
            "Echocardiogram"
        ],
        recommended_specialists=[
            "Cardiology",
            "Interventional cardiology"
        ]
    )
    
    diagnosis2 = DiagnosisResult(
        condition="Acute Anxiety",
        icd_code="F41.0",
        confidence_score=0.35,
        evidence=[
            "Diaphoresis",
            "Tachycardia"
        ],
        differential_diagnoses=["Panic disorder"]
    )
    
    # Create decision support
    decision = DecisionSupport(
        request_id=f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        patient_id=patient_id,
        timestamp=datetime.now()
    )
    
    decision.add_diagnosis(diagnosis1)
    decision.add_diagnosis(diagnosis2)
    
    decision.urgency_level = UrgencyLevel.URGENT
    decision.triage_score = 85.0
    
    decision.add_alert("CRITICAL: Suspected acute coronary syndrome - immediate cardiology consult required")
    decision.add_warning("Patient has multiple cardiovascular risk factors")
    
    decision.clinical_notes.append("Patient should be admitted to cardiac care unit")
    decision.clinical_notes.append("Continuous cardiac monitoring recommended")
    
    decision.models_used = [
        "CardioNet-v2.3",
        "ClinicalBERT-diagnosis",
        "TriageClassifier-v1.5"
    ]
    
    decision.processing_time_ms = 2847.5
    
    decision.explanation = """
    Based on the clinical presentation, ECG findings, and patient's cardiovascular risk factors,
    there is a high probability of acute coronary syndrome. The patient requires immediate
    cardiology evaluation and likely cardiac catheterization. Alternative diagnosis of anxiety
    was considered but deemed less likely given the constellation of symptoms and risk factors.
    """
    
    decision.feature_importance = {
        "chest_pain_severity": 0.35,
        "ecg_changes": 0.28,
        "cardiac_biomarkers": 0.22,
        "risk_factors": 0.10,
        "vital_signs": 0.05
    }
    
    return decision


def main():
    """Main demonstration function."""
    
    print("=" * 80)
    print("EarlyCare Gateway - Advanced MongoDB Integration Demo")
    print("=" * 80)
    
    # Initialize database
    print("\n1️⃣  Initializing MongoDB connection...")
    db = MongoDBPatientRepository(
        connection_string="mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/",
        database_name="earlycare"
    )
    print("   ✓ Connected to MongoDB")
    
    try:
        # Generate sample patients
        print("\n2️⃣  Creating sample patients...")
        patients_data = generate_sample_data()
        
        for patient_data in patients_data:
            patient = Patient(**patient_data)
            patient.calculate_age()
            
            # Save patient
            if db.save_patient(patient):
                print(f"   ✓ Patient {patient.patient_id} saved (Age: {patient.age}, Priority: {patient.chief_complaint})")
            
            # Log audit event
            db.log_audit_event(
                event_type="create",
                user_id="SYSTEM",
                action=f"Created patient record for {patient.patient_id}",
                patient_id=patient.patient_id,
                resource_type="patient",
                resource_id=patient.patient_id
            )
        
        # Process first patient with complete workflow
        print("\n3️⃣  Processing complete clinical workflow for Patient P2024001...")
        
        patient = db.get_patient("P2024001")
        if not patient:
            print("   ✗ Patient not found!")
            return
        
        # Create clinical data
        print("\n   📋 Creating clinical data...")
        clinical_data_list = create_clinical_data_examples(patient.patient_id)
        print(f"   ✓ Created {len(clinical_data_list)} clinical data entries")
        print(f"      - Text data: Admission note")
        print(f"      - Signal data: ECG (4 seconds, 1000 samples)")
        print(f"      - Image data: Chest X-ray (DICOM)")
        
        # Create patient record
        print("\n   📁 Creating patient record...")
        encounter_id = f"ENC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        patient_record = PatientRecord(
            patient=patient,
            encounter_id=encounter_id,
            encounter_timestamp=datetime.now(),
            priority="urgent"
        )
        
        # Add clinical data to record
        for data in clinical_data_list:
            patient_record.add_clinical_data(data)
        
        # Add processing context
        context = create_processing_context(patient, len(clinical_data_list))
        patient_record.metadata.update(context)
        
        # Save patient record
        if db.save_patient_record(patient_record):
            print(f"   ✓ Patient record saved: {encounter_id}")
            print(f"      - Priority: {patient_record.priority}")
            print(f"      - Clinical data: {len(patient_record.clinical_data)} entries")
            print(f"      - Triage score: {context['processing_context']['triage']['score']}")
        
        # Log audit event
        db.log_audit_event(
            event_type="process",
            user_id="SYSTEM",
            action=f"Processed clinical encounter {encounter_id}",
            patient_id=patient.patient_id,
            resource_type="encounter",
            resource_id=encounter_id
        )
        
        # Create and save decision support
        print("\n   🧠 Generating decision support...")
        decision = create_decision_support_example(patient.patient_id, encounter_id)
        
        if db.save_decision_support(decision, encounter_id):
            print(f"   ✓ Decision support saved: {decision.request_id}")
            print(f"      - Diagnoses: {len(decision.diagnoses)}")
            print(f"      - Top diagnosis: {decision.get_top_diagnosis().condition}")
            print(f"      - Confidence: {decision.get_top_diagnosis().confidence_score:.2%}")
            print(f"      - Urgency: {decision.urgency_level.value}")
            print(f"      - Processing time: {decision.processing_time_ms:.1f}ms")
        
        # Log audit event
        db.log_audit_event(
            event_type="process",
            user_id="SYSTEM",
            action=f"Generated decision support for {encounter_id}",
            patient_id=patient.patient_id,
            resource_type="decision_support",
            resource_id=decision.request_id
        )
        
        # Query and analysis
        print("\n4️⃣  Querying database...")
        
        # Get patient records
        print("\n   📊 Patient records for P2024001:")
        records = db.get_patient_records("P2024001", limit=5)
        for record in records:
            print(f"      - {record['encounter_id']}: {record['priority']} priority")
            print(f"        Timestamp: {record['encounter_timestamp']}")
            print(f"        Clinical data refs: {len(record.get('clinical_data_refs', []))}")
        
        # Get clinical data
        print("\n   📋 Clinical data for P2024001:")
        clinical_data = db.get_patient_clinical_data("P2024001", limit=10)
        print(f"      Total entries: {len(clinical_data)}")
        data_types = {}
        for data in clinical_data:
            dt = data['data_type']
            data_types[dt] = data_types.get(dt, 0) + 1
        for dt, count in data_types.items():
            print(f"      - {dt}: {count}")
        
        # Get decision support results
        print("\n   🧠 Decision support results for P2024001:")
        decisions = db.get_patient_decisions("P2024001", limit=5)
        for dec in decisions:
            print(f"      - {dec['request_id']}")
            print(f"        Urgency: {dec['urgency_level']}")
            print(f"        Diagnoses: {len(dec['diagnoses'])}")
            if dec['diagnoses']:
                top = dec['diagnoses'][0]
                print(f"        Top: {top['condition']} ({top['confidence_score']:.2%})")
        
        # Get urgent cases
        print("\n   🚨 Urgent cases across all patients:")
        urgent_records = db.find_records_by_priority("urgent", limit=10)
        print(f"      Found {len(urgent_records)} urgent cases")
        for record in urgent_records:
            print(f"      - Patient {record['patient_id']}: {record['encounter_id']}")
        
        # Get audit logs
        print("\n   📝 Recent audit logs:")
        audit_logs = db.get_audit_logs(limit=10)
        print(f"      Found {len(audit_logs)} recent events")
        for log in audit_logs[:5]:
            print(f"      - {log['timestamp']}: {log['event_type']} - {log['action']}")
        
        # Database statistics
        print("\n5️⃣  Database Statistics:")
        stats = db.get_statistics()
        print(f"   Total Patients: {stats['total_patients']}")
        print(f"   Total Clinical Data: {stats['total_clinical_data']}")
        print(f"   Total Patient Records: {stats['total_records']}")
        print(f"   Total Decisions: {stats['total_decisions']}")
        
        print("\n   Priority Distribution:")
        for priority, count in stats['priority_counts'].items():
            print(f"      - {priority}: {count}")
        
        print("\n   Clinical Data Types:")
        for data_type, count in stats['data_type_counts'].items():
            print(f"      - {data_type}: {count}")
        
        print("\n" + "=" * 80)
        print("✅ Advanced workflow demonstration completed successfully!")
        print("=" * 80)
        
        print("\n💡 Key Features Demonstrated:")
        print("   • Complete patient registration with demographics and medical history")
        print("   • Multi-modal clinical data (text, signals, images)")
        print("   • Processing context from chain of responsibility handlers")
        print("   • Decision support with diagnoses and recommendations")
        print("   • Comprehensive audit logging")
        print("   • Advanced querying and filtering")
        print("   • Statistical analysis")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔒 Closing database connection...")
        db.close()
        print("   ✓ Connection closed")


if __name__ == "__main__":
    main()
