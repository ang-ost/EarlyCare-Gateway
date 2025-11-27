"""
Quick Start Script - Run this to see the EarlyCare Gateway in action
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
from src.gateway.clinical_gateway import ClinicalGateway
from src.models.patient import Patient, PatientRecord, Gender
from src.models.clinical_data import TextData, SignalData, DataSource
from src.strategy.strategy_selector import StrategySelector
from src.observer.metrics_observer import MetricsObserver


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_section(text):
    print(f"\n--- {text} ---")


def main():
    print_header("🏥 EarlyCare Gateway - Quick Start Demo")
    
    # Setup
    print_section("Initializing Gateway")
    gateway = ClinicalGateway()
    metrics = MetricsObserver()
    gateway.attach_observer(metrics)
    
    strategy_selector = StrategySelector.create_default_selector()
    gateway.set_strategy_selector(strategy_selector)
    print("✓ Gateway initialized with monitoring and AI strategies")
    
    # Create patient
    print_section("Creating Patient Record")
    patient = Patient(
        patient_id="DEMO-001",
        date_of_birth=datetime(1970, 5, 20),
        gender=Gender.MALE,
        medical_record_number="MRN-DEMO-001",
        chief_complaint="Severe chest pain radiating to left arm",
        medical_history=["Hypertension", "Hyperlipidemia"],
        current_medications=["Lisinopril", "Atorvastatin"]
    )
    
    record = PatientRecord(patient=patient, priority="urgent")
    print(f"✓ Patient: {patient.patient_id} (Age: {patient.calculate_age()})")
    print(f"  Chief Complaint: {patient.chief_complaint}")
    
    # Add clinical data
    print_section("Adding Clinical Data")
    
    # Emergency department note
    ed_note = TextData(
        data_id="ED-NOTE-001",
        patient_id=patient.patient_id,
        timestamp=datetime.now(),
        source=DataSource.EHR,
        text_content="""
        EMERGENCY DEPARTMENT NOTE
        
        CC: Chest pain radiating to left arm
        
        HPI: 53 y/o M with PMH of HTN, hyperlipidemia presents with acute onset 
        substernal chest pain started 1 hour ago. Pain 8/10, pressure-like, radiates 
        to left arm. Associated with diaphoresis, shortness of breath, and nausea. 
        Denies recent trauma, fever, or cough.
        
        VITALS: BP 168/98, HR 105, RR 24, O2 Sat 96% RA, Temp 37.1C
        
        PHYSICAL EXAM: Diaphoretic, anxious. Cardiac: Tachycardic, regular rhythm.
        Lungs: Clear bilaterally. No peripheral edema.
        
        ASSESSMENT: Acute chest pain, concerning for acute coronary syndrome.
        Recommend immediate ECG, troponin, and cardiology consult.
        """,
        document_type="emergency_note"
    )
    record.add_clinical_data(ed_note)
    print("✓ Added emergency department clinical note")
    
    # ECG data
    ecg_signal = SignalData(
        data_id="ECG-001",
        patient_id=patient.patient_id,
        timestamp=datetime.now(),
        source=DataSource.WEARABLE,
        signal_values=[0.1, 0.15, 0.9, 0.2, -0.05, 0.0] * 100,
        sampling_rate=250.0,
        signal_type="ECG",
        units="mV",
        duration=2.4
    )
    record.add_clinical_data(ecg_signal)
    print("✓ Added ECG signal data (250 Hz, 2.4 sec)")
    
    # Process
    print_section("Processing Through Gateway Pipeline")
    print("→ Validation → Enrichment → Triage → AI Analysis")
    
    decision_support = gateway.process_request(record)
    
    # Results
    print_header("📊 DECISION SUPPORT RESULTS")
    
    print(f"\n🆔 Request ID: {decision_support.request_id}")
    print(f"⏱️  Processing Time: {decision_support.processing_time_ms:.2f}ms")
    print(f"🚨 Urgency: {decision_support.urgency_level.value.upper()}")
    print(f"📈 Triage Score: {decision_support.triage_score:.1f}/100")
    
    if decision_support.diagnoses:
        print(f"\n💊 DIAGNOSES ({len(decision_support.diagnoses)}):")
        for i, diag in enumerate(decision_support.diagnoses, 1):
            print(f"\n  {i}. {diag.condition}")
            print(f"     Confidence: {diag.confidence_score:.1%} ({diag.confidence_level.value})")
            if diag.evidence:
                print(f"     Evidence: {', '.join(diag.evidence[:2])}")
            if diag.recommended_tests:
                print(f"     Tests: {', '.join(diag.recommended_tests[:2])}")
    
    if decision_support.alerts:
        print("\n⚠️  ALERTS:")
        for alert in decision_support.alerts:
            print(f"     • {alert}")
    
    print(f"\n🤖 Models: {', '.join(decision_support.models_used)}")
    
    if decision_support.explanation:
        print(f"\n📝 Explanation: {decision_support.explanation}")
    
    # Metrics
    print_header("📈 SYSTEM METRICS")
    stats = metrics.get_metrics()
    print(f"\nRequests Processed: {stats['requests_completed']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    print(f"Avg Processing Time: {stats['avg_processing_time_ms']:.2f}ms")
    
    # Gateway status
    print_section("Gateway Health")
    health = gateway.health_check()
    print(f"Status: {health['status'].upper()} ✓")
    
    print_header("✅ Demo Complete!")
    print("\nNext steps:")
    print("  • Check out examples/ directory for more use cases")
    print("  • Read README.md for full documentation")
    print("  • Review config/ files to customize behavior")
    print("  • Explore src/ to understand the architecture")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
