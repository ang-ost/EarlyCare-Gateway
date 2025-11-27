"""
Example 1: Basic Clinical Gateway Usage
Demonstrates the core functionality of processing clinical data through the gateway.
"""

from datetime import datetime
from src.gateway.clinical_gateway import ClinicalGateway
from src.models.patient import Patient, PatientRecord, Gender
from src.models.clinical_data import TextData, SignalData, DataSource
from src.strategy.strategy_selector import StrategySelector
from src.observer.metrics_observer import MetricsObserver, AuditObserver


def main():
    print("=" * 60)
    print("EarlyCare Gateway - Basic Usage Example")
    print("=" * 60)
    
    # 1. Initialize the gateway
    print("\n1. Initializing Clinical Gateway...")
    gateway = ClinicalGateway()
    
    # 2. Set up monitoring
    print("2. Setting up monitoring observers...")
    metrics_observer = MetricsObserver()
    audit_observer = AuditObserver(log_file="examples/audit_example.log")
    
    gateway.attach_observer(metrics_observer)
    gateway.attach_observer(audit_observer)
    
    # 3. Configure model strategy
    print("3. Configuring AI model strategies...")
    strategy_selector = StrategySelector.create_default_selector()
    strategy_selector.enable_ensemble(True)
    gateway.set_strategy_selector(strategy_selector)
    
    # 4. Create patient record
    print("\n4. Creating patient record...")
    patient = Patient(
        patient_id="P12345",
        date_of_birth=datetime(1975, 6, 15),
        gender=Gender.MALE,
        medical_record_number="MRN-12345",
        chief_complaint="Chest pain and shortness of breath",
        medical_history=["Hypertension", "Type 2 Diabetes"],
        current_medications=["Metformin", "Lisinopril"],
        allergies=["Penicillin"]
    )
    
    record = PatientRecord(
        patient=patient,
        priority="urgent"
    )
    
    # 5. Add clinical data
    print("5. Adding clinical data...")
    
    # Add clinical note
    clinical_note = TextData(
        data_id="NOTE-001",
        patient_id="P12345",
        timestamp=datetime.now(),
        source=DataSource.EHR,
        text_content="""
        Patient is a 48-year-old male presenting to ED with complaints of chest pain 
        radiating to left arm for the past 2 hours. Pain described as crushing, 
        associated with shortness of breath and diaphoresis. History of hypertension 
        and diabetes. Vitals: BP 165/95, HR 102, RR 22, SpO2 94% on room air.
        """,
        document_type="emergency_note"
    )
    record.add_clinical_data(clinical_note)
    
    # Add ECG signal data
    ecg_data = SignalData(
        data_id="ECG-001",
        patient_id="P12345",
        timestamp=datetime.now(),
        source=DataSource.WEARABLE,
        signal_values=[0.1, 0.2, 0.8, 0.3, -0.1] * 100,  # Mock ECG data
        sampling_rate=250.0,  # Hz
        signal_type="ECG",
        units="mV",
        duration=2.0  # seconds
    )
    record.add_clinical_data(ecg_data)
    
    # 6. Process through gateway
    print("\n6. Processing through gateway...")
    print("-" * 60)
    
    decision_support = gateway.process_request(record)
    
    # 7. Display results
    print("\n7. DECISION SUPPORT RESULTS")
    print("-" * 60)
    print(f"Request ID: {decision_support.request_id}")
    print(f"Patient ID: {decision_support.patient_id}")
    print(f"Urgency Level: {decision_support.urgency_level.value.upper()}")
    print(f"Triage Score: {decision_support.triage_score:.1f}/100")
    print(f"Processing Time: {decision_support.processing_time_ms:.2f}ms")
    
    print(f"\nModels Used: {', '.join(decision_support.models_used)}")
    
    if decision_support.diagnoses:
        print(f"\nDIAGNOSES ({len(decision_support.diagnoses)}):")
        for i, diagnosis in enumerate(decision_support.diagnoses, 1):
            print(f"\n  {i}. {diagnosis.condition}")
            print(f"     Confidence: {diagnosis.confidence_score:.2%} ({diagnosis.confidence_level.value})")
            if diagnosis.evidence:
                print(f"     Evidence: {', '.join(diagnosis.evidence[:3])}")
            if diagnosis.recommended_tests:
                print(f"     Recommended Tests: {', '.join(diagnosis.recommended_tests[:2])}")
    
    if decision_support.alerts:
        print(f"\nALERTS:")
        for alert in decision_support.alerts:
            print(f"  ⚠️  {alert}")
    
    if decision_support.warnings:
        print(f"\nWARNINGS:")
        for warning in decision_support.warnings:
            print(f"  ⚡ {warning}")
    
    if decision_support.explanation:
        print(f"\nEXPLANATION:")
        print(f"  {decision_support.explanation}")
    
    # 8. Display metrics
    print("\n8. SYSTEM METRICS")
    print("-" * 60)
    metrics = metrics_observer.get_metrics()
    print(f"Total Requests: {metrics['requests_total']}")
    print(f"Completed: {metrics['requests_completed']}")
    print(f"Failed: {metrics['requests_failed']}")
    print(f"Success Rate: {metrics['success_rate']:.2%}")
    print(f"Avg Processing Time: {metrics['avg_processing_time_ms']:.2f}ms")
    print(f"Diagnoses Made: {metrics['diagnoses_made']}")
    
    # 9. Gateway health check
    print("\n9. GATEWAY HEALTH CHECK")
    print("-" * 60)
    health = gateway.health_check()
    print(f"Status: {health['status'].upper()}")
    print(f"Components:")
    for component, status in health['components'].items():
        status_icon = "✓" if status else "✗"
        print(f"  {status_icon} {component}: {status}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
