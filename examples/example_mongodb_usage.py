"""
Example script demonstrating MongoDB integration for patient data management.

This script shows how to:
1. Connect to MongoDB
2. Save patient information
3. Retrieve and query patient data
4. Save and retrieve patient records
5. Get database statistics

Requirements:
- MongoDB server running (default: localhost:27017)
- pymongo installed: pip install pymongo
"""

from datetime import datetime
from src.models.patient import Patient, PatientRecord, Gender
from src.models.clinical_data import ClinicalData, ClinicalDataType
from src.database.mongodb_repository import MongoDBPatientRepository


def main():
    """Main example function."""
    
    # 1. Initialize MongoDB repository
    print("Connecting to MongoDB...")
    db = MongoDBPatientRepository(
        connection_string="mongodb://localhost:27017/",
        database_name="earlycare"
    )
    
    try:
        # 2. Create and save a patient
        print("\n=== Creating Patient ===")
        patient = Patient(
            patient_id="P001",
            date_of_birth=datetime(1985, 3, 15),
            gender=Gender.FEMALE,
            medical_record_number="MRN12345",
            chief_complaint="Chest pain",
            medical_history=["Hypertension", "Type 2 Diabetes"],
            current_medications=["Metformin", "Lisinopril"],
            allergies=["Penicillin"],
            primary_language="en"
        )
        patient.calculate_age()
        
        # Save patient
        if db.save_patient(patient):
            print(f"✓ Patient {patient.patient_id} saved successfully")
        else:
            print(f"✗ Patient {patient.patient_id} already exists or error occurred")
        
        # 3. Retrieve patient
        print("\n=== Retrieving Patient ===")
        retrieved_patient = db.get_patient("P001")
        if retrieved_patient:
            print(f"Patient ID: {retrieved_patient.patient_id}")
            print(f"Age: {retrieved_patient.age}")
            print(f"Gender: {retrieved_patient.gender.value}")
            print(f"Medical History: {', '.join(retrieved_patient.medical_history)}")
            print(f"Allergies: {', '.join(retrieved_patient.allergies)}")
        
        # 4. Update patient information
        print("\n=== Updating Patient ===")
        retrieved_patient.current_medications.append("Aspirin")
        if db.update_patient(retrieved_patient):
            print("✓ Patient updated successfully")
        
        # 5. Create and save a patient record with clinical data
        print("\n=== Creating Patient Record ===")
        
        # Create clinical data
        ecg_data = ClinicalData(
            data_type=ClinicalDataType.ECG,
            timestamp=datetime.now(),
            values={"heart_rate": 85, "rhythm": "normal sinus"},
            unit="bpm",
            source="ECG Monitor"
        )
        
        vital_signs = ClinicalData(
            data_type=ClinicalDataType.VITAL_SIGNS,
            timestamp=datetime.now(),
            values={
                "blood_pressure": "130/85",
                "temperature": 37.2,
                "respiratory_rate": 16
            },
            unit="various",
            source="Bedside Monitor"
        )
        
        # Create patient record
        patient_record = PatientRecord(
            patient=patient,
            encounter_id="ENC001",
            encounter_timestamp=datetime.now(),
            priority="urgent"
        )
        patient_record.add_clinical_data(ecg_data)
        patient_record.add_clinical_data(vital_signs)
        
        # Save patient record
        if db.save_patient_record(patient_record):
            print(f"✓ Patient record {patient_record.encounter_id} saved successfully")
        
        # 6. Retrieve patient records
        print("\n=== Retrieving Patient Records ===")
        records = db.get_patient_records("P001", limit=5)
        print(f"Found {len(records)} records for patient P001")
        for record in records:
            print(f"  - Encounter: {record['encounter_id']}")
            print(f"    Priority: {record['priority']}")
            print(f"    Timestamp: {record['encounter_timestamp']}")
            print(f"    Clinical data entries: {len(record['clinical_data'])}")
        
        # 7. Query by priority
        print("\n=== Querying by Priority ===")
        urgent_records = db.find_records_by_priority("urgent", limit=10)
        print(f"Found {len(urgent_records)} urgent records")
        
        # 8. Find patients by criteria
        print("\n=== Finding Patients ===")
        # Find all female patients
        female_patients = db.find_patients({"gender": "female"})
        print(f"Found {len(female_patients)} female patients")
        
        # Find patients with specific allergies
        penicillin_allergy = db.find_patients({"allergies": "Penicillin"})
        print(f"Found {len(penicillin_allergy)} patients with Penicillin allergy")
        
        # 9. Get database statistics
        print("\n=== Database Statistics ===")
        stats = db.get_statistics()
        print(f"Total patients: {stats.get('total_patients', 0)}")
        print(f"Total records: {stats.get('total_records', 0)}")
        print("Priority distribution:")
        for priority, count in stats.get('priority_counts', {}).items():
            print(f"  - {priority}: {count}")
        
        # 10. Create additional example patients
        print("\n=== Creating Additional Patients ===")
        additional_patients = [
            Patient(
                patient_id="P002",
                date_of_birth=datetime(1990, 7, 22),
                gender=Gender.MALE,
                medical_record_number="MRN12346",
                chief_complaint="Fever and cough",
                medical_history=["Asthma"],
                current_medications=["Albuterol"],
                allergies=[]
            ),
            Patient(
                patient_id="P003",
                date_of_birth=datetime(1978, 11, 5),
                gender=Gender.FEMALE,
                medical_record_number="MRN12347",
                chief_complaint="Abdominal pain",
                medical_history=["Gastritis"],
                current_medications=["Omeprazole"],
                allergies=["Sulfa drugs"]
            )
        ]
        
        for pat in additional_patients:
            pat.calculate_age()
            if db.save_patient(pat):
                print(f"✓ Patient {pat.patient_id} saved")
        
        print("\n=== Example Complete ===")
        print("MongoDB integration is working correctly!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connection
        print("\nClosing database connection...")
        db.close()


if __name__ == "__main__":
    main()
