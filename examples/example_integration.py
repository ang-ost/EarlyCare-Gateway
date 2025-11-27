"""
Example 2: Clinical System Integration
Demonstrates integration with HL7, FHIR, and DICOM systems.
"""

from datetime import datetime
from src.gateway.clinical_gateway import ClinicalGateway
from src.facade.clinical_facade import ClinicalSystemFacade
from src.strategy.strategy_selector import StrategySelector
from src.observer.metrics_observer import AuditObserver


def main():
    print("=" * 60)
    print("EarlyCare Gateway - Clinical System Integration Example")
    print("=" * 60)
    
    # 1. Initialize gateway and facade
    print("\n1. Initializing systems...")
    gateway = ClinicalGateway()
    facade = ClinicalSystemFacade()
    
    # Set up audit logging
    audit = AuditObserver(log_file="examples/integration_audit.log")
    gateway.attach_observer(audit)
    
    # Configure strategy
    strategy_selector = StrategySelector.create_default_selector()
    gateway.set_strategy_selector(strategy_selector)
    
    # 2. Connect to FHIR server
    print("\n2. Connecting to FHIR server...")
    fhir_config = {
        'base_url': 'https://fhir.hospital.org/api/r4',
        'api_key': 'demo-api-key-12345'
    }
    
    if facade.connect_to_system('fhir', fhir_config):
        print("   ✓ Connected to FHIR server")
    else:
        print("   ✗ Failed to connect to FHIR server")
    
    # 3. Connect to HL7 system
    print("\n3. Connecting to HL7 system...")
    hl7_config = {
        'host': 'hl7.hospital.local',
        'port': 2575,
        'sending_application': 'EARLYCARE',
        'sending_facility': 'GATEWAY'
    }
    
    if facade.connect_to_system('hl7', hl7_config):
        print("   ✓ Connected to HL7 system")
    else:
        print("   ✗ Failed to connect to HL7 system")
    
    # 4. Connect to PACS
    print("\n4. Connecting to DICOM PACS...")
    dicom_config = {
        'ae_title': 'EARLYCARE_SCU',
        'peer_ae_title': 'HOSPITAL_PACS',
        'host': 'pacs.hospital.local',
        'port': 11112
    }
    
    if facade.connect_to_system('dicom', dicom_config):
        print("   ✓ Connected to DICOM PACS")
    else:
        print("   ✗ Failed to connect to DICOM PACS")
    
    # 5. Check system status
    print("\n5. System Status:")
    print("-" * 60)
    status = facade.get_system_status()
    
    print("Connected Systems:")
    for system, connected in status['connected_systems'].items():
        status_icon = "✓" if connected else "✗"
        print(f"  {status_icon} {system.upper()}: {'Connected' if connected else 'Disconnected'}")
    
    print("\nSystem Details:")
    print(f"  FHIR: {status['fhir_status']['protocol']} @ {status['fhir_status']['base_url']}")
    print(f"  HL7: {status['hl7_status']['protocol']}")
    print(f"  DICOM: {status['dicom_status']['protocol']}")
    
    # 6. Import patient data from FHIR
    print("\n6. Importing patient data from FHIR...")
    patient_id = "Patient-12345"
    
    try:
        record = facade.import_patient_data(
            system_type='fhir',
            patient_id=patient_id,
            data_types=['Observation', 'DiagnosticReport', 'DocumentReference']
        )
        
        print(f"   ✓ Imported patient record")
        print(f"     Patient ID: {record.patient.patient_id}")
        print(f"     Clinical Data Items: {len(record.clinical_data)}")
    except Exception as e:
        print(f"   ✗ Error importing data: {e}")
        return
    
    # 7. Process through gateway
    print("\n7. Processing through gateway...")
    decision_support = gateway.process_request(record)
    
    print(f"   ✓ Processing complete")
    print(f"     Request ID: {decision_support.request_id}")
    print(f"     Urgency: {decision_support.urgency_level.value}")
    print(f"     Diagnoses: {len(decision_support.diagnoses)}")
    
    # 8. Export results back to FHIR
    print("\n8. Exporting results to FHIR...")
    try:
        success = facade.export_decision_support(
            system_type='fhir',
            decision_support=decision_support,
            destination=patient_id
        )
        
        if success:
            print("   ✓ Results exported successfully")
        else:
            print("   ✗ Failed to export results")
    except Exception as e:
        print(f"   ✗ Error exporting: {e}")
    
    # 9. Export results to HL7
    print("\n9. Exporting results via HL7...")
    try:
        success = facade.export_decision_support(
            system_type='hl7',
            decision_support=decision_support,
            destination='RECEIVING_SYSTEM'
        )
        
        if success:
            print("   ✓ HL7 message sent successfully")
        else:
            print("   ✗ Failed to send HL7 message")
    except Exception as e:
        print(f"   ✗ Error sending HL7: {e}")
    
    # 10. Query clinical data
    print("\n10. Querying additional data...")
    try:
        results = facade.query_clinical_data(
            system_type='fhir',
            query_params={
                'patient': patient_id,
                'category': 'laboratory'
            }
        )
        print(f"   ✓ Found {len(results)} matching records")
    except Exception as e:
        print(f"   ✗ Query error: {e}")
    
    # 11. Cleanup
    print("\n11. Disconnecting from systems...")
    facade.disconnect_all()
    print("   ✓ All connections closed")
    
    print("\n" + "=" * 60)
    print("Integration example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
