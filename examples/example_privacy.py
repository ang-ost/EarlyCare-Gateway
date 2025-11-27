"""
Example 3: Privacy and Security Features
Demonstrates anonymization, encryption, and audit logging.
"""

from datetime import datetime
from src.privacy.anonymizer import DataAnonymizer
from src.privacy.encryption import EncryptionService
from src.privacy.audit import AuditLogger, AuditEventType
from src.models.patient import Patient, PatientRecord, Gender
from src.models.clinical_data import TextData, DataSource


def main():
    print("=" * 60)
    print("EarlyCare Gateway - Privacy & Security Example")
    print("=" * 60)
    
    # 1. Data Anonymization
    print("\n1. DATA ANONYMIZATION")
    print("-" * 60)
    
    anonymizer = DataAnonymizer()
    
    # Anonymize text with PII
    original_text = """
    Patient John Doe, age 45, SSN 123-45-6789, presented to clinic.
    Contact number: 555-123-4567
    Email: john.doe@email.com
    Medical Record: MRN1234567
    """
    
    print("Original Text (contains PII):")
    print(original_text)
    
    anonymized_text = anonymizer.anonymize_text(original_text)
    
    print("\nAnonymized Text:")
    print(anonymized_text)
    
    # Detect PII
    print("\n\nPII Detection:")
    pii_found = anonymizer.detect_pii(original_text)
    for item in pii_found:
        print(f"  - {item['type'].upper()}: {item['value']}")
    
    # Generate pseudonyms
    print("\n\nPseudonym Generation:")
    patient_id = "P12345"
    pseudonym = anonymizer.generate_pseudonym(patient_id, "patient")
    print(f"  Original ID: {patient_id}")
    print(f"  Pseudonym: {pseudonym}")
    
    # Age binning
    print("\n\nAge Anonymization:")
    ages = [25, 45, 67, 85, 92]
    for age in ages:
        binned = anonymizer.anonymize_age(age)
        print(f"  Age {age} → {binned}")
    
    # 2. Encryption
    print("\n\n2. DATA ENCRYPTION")
    print("-" * 60)
    
    encryption = EncryptionService()
    
    # Encrypt sensitive text
    sensitive_data = "Patient has history of HIV and hepatitis C"
    print(f"Original: {sensitive_data}")
    
    encrypted = encryption.encrypt(sensitive_data)
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = encryption.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Key information
    print("\n\nEncryption Key Info:")
    key_info = encryption.get_key_info()
    for key, value in key_info.items():
        print(f"  {key}: {value}")
    
    # Hash data
    print("\n\nData Hashing:")
    data_to_hash = "patient-identifier-12345"
    hash_value = encryption.hash_data(data_to_hash, 'sha256')
    print(f"  Data: {data_to_hash}")
    print(f"  SHA-256: {hash_value[:32]}...")
    
    # 3. Audit Logging
    print("\n\n3. AUDIT LOGGING")
    print("-" * 60)
    
    audit = AuditLogger(log_directory="examples/audit_logs")
    
    # Log various events
    print("\nLogging audit events...")
    
    # Data access
    audit.log_data_access(
        user_id="DR-001",
        patient_id="P12345",
        data_type="clinical_notes",
        purpose="diagnosis",
        outcome="success"
    )
    print("  ✓ Logged data access event")
    
    # Model execution
    audit.log_model_execution(
        user_id="DR-001",
        patient_id="P12345",
        model_name="cardiology_model_v2",
        request_id="REQ-98765",
        outcome="success",
        processing_time_ms=1234.56
    )
    print("  ✓ Logged model execution event")
    
    # Data export
    audit.log_data_export(
        user_id="DR-001",
        patient_id="P12345",
        export_format="FHIR",
        destination="research_database",
        outcome="success"
    )
    print("  ✓ Logged data export event")
    
    # Authentication
    audit.log_authentication(
        user_id="DR-001",
        action="login",
        source_ip="192.168.1.100",
        outcome="success"
    )
    print("  ✓ Logged authentication event")
    
    # Consent change
    audit.log_consent_change(
        user_id="DR-001",
        patient_id="P12345",
        consent_type="research",
        consent_status=True,
        outcome="success"
    )
    print("  ✓ Logged consent change event")
    
    # Query audit logs
    print("\n\nQuerying Audit Logs:")
    recent_logs = audit.query_logs()
    print(f"  Total audit entries: {len(recent_logs)}")
    
    # Get patient-specific audit trail
    patient_logs = audit.get_patient_access_log("P12345", days=30)
    print(f"  Patient P12345 access logs: {len(patient_logs)}")
    
    if patient_logs:
        print("\n  Recent patient access events:")
        for log in patient_logs[:3]:
            print(f"    - {log['event_type']}: {log['action']} by {log['user_id']}")
    
    # 4. Full Patient Record Anonymization
    print("\n\n4. PATIENT RECORD ANONYMIZATION")
    print("-" * 60)
    
    # Create patient record
    patient = Patient(
        patient_id="P12345",
        date_of_birth=datetime(1975, 6, 15),
        gender=Gender.MALE,
        medical_record_number="MRN-12345",
        chief_complaint="Chest pain",
        medical_history=["Hypertension", "Diabetes"]
    )
    
    record = PatientRecord(patient=patient)
    
    # Add clinical data
    clinical_note = TextData(
        data_id="NOTE-001",
        patient_id="P12345",
        timestamp=datetime.now(),
        source=DataSource.EHR,
        text_content="Patient John Doe presents with chest pain. Call 555-1234.",
        document_type="clinical_note"
    )
    record.add_clinical_data(clinical_note)
    
    print("Original Patient Record:")
    print(f"  Patient ID: {record.patient.patient_id}")
    print(f"  MRN: {record.patient.medical_record_number}")
    print(f"  DOB: {record.patient.date_of_birth.strftime('%Y-%m-%d')}")
    print(f"  Clinical Data Items: {len(record.clinical_data)}")
    
    # Anonymize record
    anonymized_record = record.anonymize()
    
    print("\n\nAnonymized Patient Record:")
    print(f"  Patient ID: {anonymized_record.patient.patient_id}")
    print(f"  MRN: {anonymized_record.patient.medical_record_number}")
    print(f"  DOB: {anonymized_record.patient.date_of_birth.strftime('%Y-%m-%d')} (year only)")
    print(f"  Clinical Data Items: {len(anonymized_record.clinical_data)}")
    
    # 5. K-Anonymity
    print("\n\n5. K-ANONYMITY")
    print("-" * 60)
    
    # Sample dataset
    patient_records = [
        {'patient_id': 'P1', 'age': 25, 'zip_code': '12345', 'diagnosis': 'flu'},
        {'patient_id': 'P2', 'age': 27, 'zip_code': '12346', 'diagnosis': 'cold'},
        {'patient_id': 'P3', 'age': 45, 'zip_code': '12345', 'diagnosis': 'diabetes'},
        {'patient_id': 'P4', 'age': 47, 'zip_code': '12347', 'diagnosis': 'hypertension'},
        {'patient_id': 'P5', 'age': 67, 'zip_code': '12345', 'diagnosis': 'arthritis'},
    ]
    
    print("Original Dataset:")
    for record in patient_records[:3]:
        print(f"  {record}")
    
    # Apply k-anonymity
    k_anon_records = anonymizer.k_anonymize(
        patient_records,
        quasi_identifiers=['age', 'zip_code'],
        k=5
    )
    
    print("\n\nK-Anonymized Dataset (k=5):")
    for record in k_anon_records[:3]:
        print(f"  {record}")
    
    print("\n" + "=" * 60)
    print("Privacy & Security example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
