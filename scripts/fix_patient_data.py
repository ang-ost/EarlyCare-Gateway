"""
Script to check and fix patient data in MongoDB.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.mongodb_repository import MongoDBPatientRepository
from pymongo import MongoClient

def check_patients():
    """Check all patients in database."""
    try:
        connection_string = "mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/"
        db = MongoDBPatientRepository(connection_string=connection_string, database_name="earlycare")
        
        # Get all patients directly from collection
        patients = list(db.patients_collection.find())
        
        print(f"\n{'='*60}")
        print(f"PAZIENTI NEL DATABASE: {len(patients)}")
        print(f"{'='*60}\n")
        
        for idx, patient_data in enumerate(patients, 1):
            print(f"--- Paziente #{idx} ---")
            print(f"patient_id: {patient_data.get('patient_id')}")
            print(f"nome: '{patient_data.get('nome')}'")
            print(f"cognome: '{patient_data.get('cognome')}'")
            print(f"codice_fiscale: '{patient_data.get('codice_fiscale')}'")
            print(f"comune_nascita: '{patient_data.get('comune_nascita')}'")
            print(f"data_nascita: {patient_data.get('data_nascita')}")
            print(f"allergie: {patient_data.get('allergie')}")
            print(f"malattie_permanenti: {patient_data.get('malattie_permanenti')}")
            print(f"\nTutti i campi nel database:")
            for key, value in patient_data.items():
                if key != '_id':
                    print(f"  {key}: {value}")
            print()
        
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()

def delete_all_patients():
    """Delete all patients from database."""
    try:
        connection_string = "mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/"
        db = MongoDBPatientRepository(connection_string=connection_string, database_name="earlycare")
        
        response = input("\n⚠️  ATTENZIONE: Vuoi eliminare TUTTI i pazienti dal database? (sì/no): ")
        if response.lower() in ['sì', 'si', 'yes']:
            result = db.patients_collection.delete_many({})
            print(f"✓ Eliminati {result.deleted_count} pazienti")
        else:
            print("Operazione annullata")
    
    except Exception as e:
        print(f"Errore: {e}")

def delete_all_records():
    """Delete all patient records (clinical records) from database."""
    try:
        connection_string = "mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/"
        db = MongoDBPatientRepository(connection_string=connection_string, database_name="earlycare")
        
        response = input("\n⚠️  ATTENZIONE: Vuoi eliminare TUTTE le schede cliniche dal database? (sì/no): ")
        if response.lower() in ['sì', 'si', 'yes']:
            result = db.patient_records_collection.delete_many({})
            print(f"✓ Eliminate {result.deleted_count} schede cliniche")
        else:
            print("Operazione annullata")
    
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    print("\n=== CONTROLLO DATABASE PAZIENTI ===\n")
    print("1. Controlla pazienti nel database")
    print("2. Elimina tutti i pazienti")
    print("3. Elimina tutte le schede cliniche")
    print("0. Esci")
    
    choice = input("\nScelta: ")
    
    if choice == "1":
        check_patients()
    elif choice == "2":
        delete_all_patients()
    elif choice == "3":
        delete_all_records()
    else:
        print("Uscita...")
