"""
Script interattivo per visualizzare i documenti nel database MongoDB.

Uso:
    python scripts/view_database.py
    python scripts/view_database.py --collection patients
    python scripts/view_database.py --collection patients --limit 5
    python scripts/view_database.py --patient-id P2024001
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.mongodb_repository import MongoDBPatientRepository
import argparse


def format_date(obj):
    """Convert datetime objects to string for JSON serialization."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def print_document(doc, indent=0):
    """Pretty print a MongoDB document."""
    if doc is None:
        print("  No document found")
        return
    
    # Remove MongoDB _id for cleaner display
    if '_id' in doc:
        del doc['_id']
    
    # Convert to JSON with proper formatting
    json_str = json.dumps(doc, indent=2, default=format_date, ensure_ascii=False)
    
    # Add indentation
    lines = json_str.split('\n')
    for line in lines:
        print(' ' * indent + line)


def view_all_collections(db):
    """Show summary of all collections."""
    print("\n" + "=" * 80)
    print("DATABASE OVERVIEW - earlycare")
    print("=" * 80)
    
    stats = db.get_statistics()
    
    print("\n📊 STATISTICS:")
    print(f"   Total Patients: {stats.get('total_patients', 0)}")
    print(f"   Total Clinical Data: {stats.get('total_clinical_data', 0)}")
    print(f"   Total Patient Records: {stats.get('total_records', 0)}")
    print(f"   Total Decisions: {stats.get('total_decisions', 0)}")
    
    if stats.get('priority_counts'):
        print("\n   Priority Distribution:")
        for priority, count in stats['priority_counts'].items():
            bar = "█" * min(count, 50)
            print(f"      {priority:10s}: {count:4d} {bar}")
    
    if stats.get('data_type_counts'):
        print("\n   Clinical Data Types:")
        for data_type, count in stats['data_type_counts'].items():
            bar = "█" * min(count // 10, 50)
            print(f"      {data_type:10s}: {count:4d} {bar}")
    
    print("\n" + "=" * 80)


def view_collection(db, collection_name, limit=10, query=None):
    """View documents from a specific collection."""
    print(f"\n{'=' * 80}")
    print(f"COLLECTION: {collection_name}")
    print("=" * 80)
    
    collection = db.db[collection_name]
    
    if query:
        cursor = collection.find(query).limit(limit)
        print(f"\nQuery: {query}")
    else:
        cursor = collection.find().limit(limit)
    
    docs = list(cursor)
    
    if not docs:
        print("\n❌ No documents found")
        return
    
    print(f"\nFound {len(docs)} documents (showing up to {limit}):\n")
    
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Document {i} ---")
        print_document(doc, indent=2)
        
        if i < len(docs):
            print()


def view_patient(db, patient_id):
    """View complete information for a specific patient."""
    print(f"\n{'=' * 80}")
    print(f"PATIENT DETAILS: {patient_id}")
    print("=" * 80)
    
    # Get patient
    patient = db.get_patient(patient_id)
    if not patient:
        print(f"\n❌ Patient {patient_id} not found")
        return
    
    print("\n👤 PATIENT INFORMATION:")
    patient_dict = {
        "patient_id": patient.patient_id,
        "age": patient.age,
        "gender": patient.gender.value,
        "date_of_birth": patient.date_of_birth,
        "medical_record_number": patient.medical_record_number,
        "chief_complaint": patient.chief_complaint,
        "medical_history": patient.medical_history,
        "current_medications": patient.current_medications,
        "allergies": patient.allergies
    }
    print_document(patient_dict, indent=2)
    
    # Get clinical data
    print("\n\n📋 CLINICAL DATA:")
    clinical_data = db.get_patient_clinical_data(patient_id, limit=10)
    if clinical_data:
        print(f"   Total entries: {len(clinical_data)}")
        for i, data in enumerate(clinical_data[:5], 1):
            print(f"\n   --- Clinical Data {i} ---")
            print(f"      Type: {data['data_type']}")
            print(f"      Timestamp: {data['timestamp']}")
            print(f"      Source: {data['source']}")
            if 'document_type' in data:
                print(f"      Document Type: {data['document_type']}")
            if 'signal_type' in data:
                print(f"      Signal Type: {data['signal_type']}")
            if 'modality' in data:
                print(f"      Modality: {data['modality']}")
    else:
        print("   No clinical data found")
    
    # Get patient records
    print("\n\n📁 PATIENT RECORDS:")
    records = db.get_patient_records(patient_id, limit=5)
    if records:
        print(f"   Total records: {len(records)}")
        for i, record in enumerate(records, 1):
            print(f"\n   --- Record {i} ---")
            print(f"      Encounter ID: {record['encounter_id']}")
            print(f"      Priority: {record['priority']}")
            print(f"      Timestamp: {record['encounter_timestamp']}")
            print(f"      Clinical data refs: {len(record.get('clinical_data_refs', []))}")
            
            if 'processing_context' in record and 'triage' in record['processing_context']:
                triage = record['processing_context']['triage']
                print(f"      Triage score: {triage.get('score', 'N/A')}")
    else:
        print("   No patient records found")
    
    # Get decisions
    print("\n\n🧠 DECISION SUPPORT:")
    decisions = db.get_patient_decisions(patient_id, limit=5)
    if decisions:
        print(f"   Total decisions: {len(decisions)}")
        for i, decision in enumerate(decisions, 1):
            print(f"\n   --- Decision {i} ---")
            print(f"      Request ID: {decision['request_id']}")
            print(f"      Urgency: {decision['urgency_level']}")
            print(f"      Triage Score: {decision['triage_score']}")
            print(f"      Diagnoses: {len(decision['diagnoses'])}")
            
            if decision['diagnoses']:
                top = decision['diagnoses'][0]
                print(f"\n      Top Diagnosis:")
                print(f"         Condition: {top['condition']}")
                print(f"         Confidence: {top['confidence_score']:.2%}")
                print(f"         ICD Code: {top.get('icd_code', 'N/A')}")
            
            if decision['alerts']:
                print(f"\n      🚨 Alerts: {len(decision['alerts'])}")
                for alert in decision['alerts']:
                    print(f"         - {alert}")
    else:
        print("   No decision support found")
    
    # Get audit logs
    print("\n\n📝 AUDIT LOGS (Recent):")
    logs = db.get_audit_logs(patient_id=patient_id, limit=5)
    if logs:
        print(f"   Total logs: {len(logs)}")
        for i, log in enumerate(logs, 1):
            print(f"\n   --- Log {i} ---")
            print(f"      Timestamp: {log['timestamp']}")
            print(f"      Event Type: {log['event_type']}")
            print(f"      User: {log['user_id']}")
            print(f"      Action: {log['action']}")
            print(f"      Success: {log['success']}")
    else:
        print("   No audit logs found")
    
    print("\n" + "=" * 80)


def list_patients(db, limit=20):
    """List all patients with basic info."""
    print(f"\n{'=' * 80}")
    print("ALL PATIENTS")
    print("=" * 80)
    
    patients = db.find_patients({})[:limit]
    
    if not patients:
        print("\n❌ No patients found")
        return
    
    print(f"\nFound {len(patients)} patients:\n")
    
    for i, patient in enumerate(patients, 1):
        print(f"{i:3d}. {patient.patient_id:15s} | "
              f"Age: {patient.age or 'N/A':3} | "
              f"Gender: {patient.gender.value:8s} | "
              f"MRN: {patient.medical_record_number:15s} | "
              f"Complaint: {(patient.chief_complaint or 'N/A')[:40]}")
    
    print("\n" + "=" * 80)


def search_records_by_priority(db, priority, limit=20):
    """Search patient records by priority."""
    print(f"\n{'=' * 80}")
    print(f"RECORDS WITH PRIORITY: {priority.upper()}")
    print("=" * 80)
    
    records = db.find_records_by_priority(priority, limit=limit)
    
    if not records:
        print(f"\n❌ No {priority} records found")
        return
    
    print(f"\nFound {len(records)} records:\n")
    
    for i, record in enumerate(records, 1):
        print(f"{i:3d}. Encounter: {record['encounter_id']:20s} | "
              f"Patient: {record['patient_id']:15s} | "
              f"Time: {record['encounter_timestamp']} | "
              f"Priority: {record['priority']}")
        
        if 'processing_context' in record and 'triage' in record['processing_context']:
            score = record['processing_context']['triage'].get('score', 'N/A')
            print(f"      Triage Score: {score}")
    
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="View documents in EarlyCare MongoDB database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/view_database.py                          # Overview
  python scripts/view_database.py --list-patients          # List all patients
  python scripts/view_database.py --patient-id P2024001    # View specific patient
  python scripts/view_database.py --collection patients    # View collection
  python scripts/view_database.py --priority urgent        # View urgent records
  python scripts/view_database.py --collection clinical_data --limit 3
        """
    )
    
    parser.add_argument(
        "--connection",
        default="mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/",
        help="MongoDB connection string"
    )
    parser.add_argument(
        "--database",
        default="earlycare",
        help="Database name"
    )
    parser.add_argument(
        "--collection",
        choices=['patients', 'clinical_data', 'patient_records', 
                'decision_support', 'audit_logs'],
        help="View specific collection"
    )
    parser.add_argument(
        "--patient-id",
        help="View complete information for a specific patient"
    )
    parser.add_argument(
        "--list-patients",
        action="store_true",
        help="List all patients"
    )
    parser.add_argument(
        "--priority",
        choices=['routine', 'soon', 'urgent', 'emergency'],
        help="Search records by priority"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of documents to display"
    )
    
    args = parser.parse_args()
    
    try:
        # Connect to database
        print(f"\n🔌 Connecting to MongoDB...")
        print(f"   Connection: {args.connection}")
        print(f"   Database: {args.database}")
        
        db = MongoDBPatientRepository(
            connection_string=args.connection,
            database_name=args.database
        )
        
        print("   ✓ Connected successfully\n")
        
        # Execute requested action
        if args.patient_id:
            view_patient(db, args.patient_id)
        
        elif args.list_patients:
            list_patients(db, args.limit)
        
        elif args.priority:
            search_records_by_priority(db, args.priority, args.limit)
        
        elif args.collection:
            view_collection(db, args.collection, args.limit)
        
        else:
            # Default: show overview
            view_all_collections(db)
            print("\n💡 Tip: Use --help to see all available options")
            print("   Example: python scripts/view_database.py --list-patients")
        
        # Close connection
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
