"""
Script per eliminare record dal database MongoDB.

Uso:
    python scripts/delete_records.py --patient-id P2024001
    python scripts/delete_records.py --patient-id P2024001 --cascade
    python scripts/delete_records.py --list-patients
"""

import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.database.mongodb_repository import MongoDBPatientRepository


def list_patients(db, limit=50):
    """List all patients."""
    print("\n" + "=" * 80)
    print("PAZIENTI NEL DATABASE")
    print("=" * 80 + "\n")
    
    patients = db.find_patients({})[:limit]
    
    if not patients:
        print("❌ Nessun paziente trovato nel database\n")
        return
    
    print(f"Trovati {len(patients)} pazienti:\n")
    
    for i, patient in enumerate(patients, 1):
        print(f"{i:3d}. ID: {patient.patient_id:20s} | "
              f"MRN: {patient.medical_record_number:15s} | "
              f"Age: {patient.age or 'N/A':3} | "
              f"Gender: {patient.gender.value:8s}")
    
    print("\n" + "=" * 80 + "\n")


def delete_patient(db, patient_id, cascade=False):
    """
    Delete a patient and optionally related data.
    
    Args:
        db: Database repository
        patient_id: Patient identifier
        cascade: If True, also delete related clinical data, records, etc.
    """
    print(f"\n🗑️  Eliminazione paziente: {patient_id}")
    print("=" * 80)
    
    # Check if patient exists
    patient = db.get_patient(patient_id)
    if not patient:
        print(f"\n❌ Paziente {patient_id} non trovato nel database\n")
        return False
    
    # Show patient info
    print(f"\n👤 Paziente da eliminare:")
    print(f"   ID: {patient.patient_id}")
    print(f"   MRN: {patient.medical_record_number}")
    print(f"   Age: {patient.age}")
    print(f"   Gender: {patient.gender.value}")
    print(f"   Chief Complaint: {patient.chief_complaint or 'N/A'}")
    
    if cascade:
        # Count related records
        clinical_data_count = len(db.get_patient_clinical_data(patient_id, limit=1000))
        records_count = len(db.get_patient_records(patient_id, limit=1000))
        decisions_count = len(db.get_patient_decisions(patient_id, limit=1000))
        audit_logs_count = len(db.get_audit_logs(patient_id=patient_id, limit=1000))
        
        print(f"\n📊 Dati associati che verranno eliminati:")
        print(f"   - Clinical Data: {clinical_data_count}")
        print(f"   - Patient Records: {records_count}")
        print(f"   - Decision Support: {decisions_count}")
        print(f"   - Audit Logs: {audit_logs_count}")
    
    # Confirm deletion
    print(f"\n⚠️  ATTENZIONE: Questa operazione è IRREVERSIBILE!")
    response = input("\nConfermi l'eliminazione? (scrivi 'SI' per confermare): ")
    
    if response.strip().upper() != 'SI':
        print("\n❌ Operazione annullata\n")
        return False
    
    # Delete patient
    print(f"\n🗑️  Eliminazione in corso...")
    
    deleted_items = {
        'patient': False,
        'clinical_data': 0,
        'patient_records': 0,
        'decision_support': 0,
        'audit_logs': 0
    }
    
    try:
        if cascade:
            # Delete clinical data
            clinical_data = db.get_patient_clinical_data(patient_id, limit=1000)
            for data in clinical_data:
                if db.delete_clinical_data(data['data_id']):
                    deleted_items['clinical_data'] += 1
            
            # Delete patient records
            records = db.get_patient_records(patient_id, limit=1000)
            for record in records:
                result = db.patient_records_collection.delete_one(
                    {"encounter_id": record['encounter_id']}
                )
                if result.deleted_count > 0:
                    deleted_items['patient_records'] += 1
            
            # Delete decision support
            decisions = db.get_patient_decisions(patient_id, limit=1000)
            for decision in decisions:
                result = db.decision_support_collection.delete_one(
                    {"request_id": decision['request_id']}
                )
                if result.deleted_count > 0:
                    deleted_items['decision_support'] += 1
            
            # Note: We don't delete audit logs for compliance reasons
            print("   ℹ️  Nota: I log di audit vengono mantenuti per compliance")
        
        # Delete patient
        if db.delete_patient(patient_id):
            deleted_items['patient'] = True
            
            # Log deletion
            db.log_audit_event(
                event_type="delete",
                user_id="SCRIPT",
                action=f"Deleted patient {patient_id}" + (" with cascade" if cascade else ""),
                patient_id=patient_id,
                resource_type="patient",
                resource_id=patient_id,
                success=True,
                metadata={'cascade': cascade, 'deleted_items': deleted_items}
            )
            
            print(f"\n✅ Paziente eliminato con successo!")
            
            if cascade:
                print(f"\n📊 Elementi eliminati:")
                print(f"   - Paziente: ✓")
                print(f"   - Clinical Data: {deleted_items['clinical_data']}")
                print(f"   - Patient Records: {deleted_items['patient_records']}")
                print(f"   - Decision Support: {deleted_items['decision_support']}")
            
            print()
            return True
        else:
            print(f"\n❌ Errore durante l'eliminazione del paziente\n")
            return False
            
    except Exception as e:
        print(f"\n❌ Errore durante l'eliminazione: {e}\n")
        
        # Log failed deletion
        db.log_audit_event(
            event_type="delete",
            user_id="SCRIPT",
            action=f"Failed to delete patient {patient_id}",
            patient_id=patient_id,
            resource_type="patient",
            resource_id=patient_id,
            success=False,
            error_message=str(e)
        )
        
        return False


def delete_clinical_data_by_id(db, data_id):
    """Delete specific clinical data."""
    print(f"\n🗑️  Eliminazione clinical data: {data_id}")
    
    # Check if exists
    data = db.get_clinical_data(data_id)
    if not data:
        print(f"❌ Clinical data {data_id} non trovato\n")
        return False
    
    print(f"\n📋 Dati da eliminare:")
    print(f"   Data ID: {data['data_id']}")
    print(f"   Patient ID: {data['patient_id']}")
    print(f"   Type: {data['data_type']}")
    print(f"   Timestamp: {data['timestamp']}")
    
    response = input("\nConfermi l'eliminazione? (scrivi 'SI' per confermare): ")
    
    if response.strip().upper() != 'SI':
        print("\n❌ Operazione annullata\n")
        return False
    
    if db.delete_clinical_data(data_id):
        print(f"\n✅ Clinical data eliminato con successo!\n")
        
        db.log_audit_event(
            event_type="delete",
            user_id="SCRIPT",
            action=f"Deleted clinical data {data_id}",
            patient_id=data['patient_id'],
            resource_type="clinical_data",
            resource_id=data_id,
            success=True
        )
        
        return True
    else:
        print(f"\n❌ Errore durante l'eliminazione\n")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Elimina record dal database MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Lista tutti i pazienti
  python scripts/delete_records.py --list-patients
  
  # Elimina solo il paziente (mantiene i dati correlati)
  python scripts/delete_records.py --patient-id P2024001
  
  # Elimina paziente e tutti i dati correlati
  python scripts/delete_records.py --patient-id P2024001 --cascade
  
  # Elimina un clinical data specifico
  python scripts/delete_records.py --clinical-data-id TXT-P2024001-20241202143022
        """
    )
    
    parser.add_argument(
        "--connection",
        default=Config.MONGODB_CONNECTION_STRING,
        help="MongoDB connection string (default: from .env)"
    )
    parser.add_argument(
        "--database",
        default="earlycare",
        help="Database name"
    )
    parser.add_argument(
        "--list-patients",
        action="store_true",
        help="Lista tutti i pazienti"
    )
    parser.add_argument(
        "--patient-id",
        help="ID del paziente da eliminare"
    )
    parser.add_argument(
        "--cascade",
        action="store_true",
        help="Elimina anche tutti i dati correlati (clinical data, records, decisions)"
    )
    parser.add_argument(
        "--clinical-data-id",
        help="ID del clinical data da eliminare"
    )
    
    args = parser.parse_args()
    
    try:
        # Connect to database
        print(f"\n🔌 Connessione a MongoDB...")
        print(f"   Connection: {args.connection}")
        print(f"   Database: {args.database}")
        
        db = MongoDBPatientRepository(
            connection_string=args.connection,
            database_name=args.database
        )
        
        print("   ✓ Connesso con successo")
        
        # Execute requested action
        if args.list_patients:
            list_patients(db)
        
        elif args.patient_id:
            success = delete_patient(db, args.patient_id, args.cascade)
            sys.exit(0 if success else 1)
        
        elif args.clinical_data_id:
            success = delete_clinical_data_by_id(db, args.clinical_data_id)
            sys.exit(0 if success else 1)
        
        else:
            print("\n⚠️  Specificare --list-patients, --patient-id, o --clinical-data-id")
            print("   Usa --help per vedere tutte le opzioni\n")
            sys.exit(1)
        
        # Close connection
        db.close()
        
    except Exception as e:
        print(f"\n❌ Errore: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
