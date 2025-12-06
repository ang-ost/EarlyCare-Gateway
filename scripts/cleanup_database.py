"""
Script per pulire le collezioni obsolete dal database MongoDB.

Questo script elimina:
- clinical_data (ora integrata in patient_records)
- decision_support (non più utilizzata)
- audit_logs (non più utilizzata)

Uso:
    python scripts/cleanup_database.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from pymongo import MongoClient
import argparse


def cleanup_collections(connection_string: str, database_name: str = "earlycare"):
    """
    Remove obsolete collections from MongoDB.
    
    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database
    """
    try:
        print(f"\n🔌 Connessione a MongoDB...")
        print(f"   Database: {database_name}")
        
        # Connect with SSL workaround
        client = MongoClient(
            connection_string,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=10000
        )
        
        db = client[database_name]
        
        # Test connection
        client.admin.command('ping')
        print("   ✓ Connesso con successo\n")
        
        # Get current collections
        existing_collections = db.list_collection_names()
        print(f"📋 Collezioni esistenti: {', '.join(existing_collections)}\n")
        
        # Collections to remove
        obsolete_collections = ['clinical_data', 'decision_support', 'audit_logs']
        
        removed_count = 0
        for collection_name in obsolete_collections:
            if collection_name in existing_collections:
                print(f"🗑️  Rimozione collezione: {collection_name}")
                
                # Get document count before deletion
                doc_count = db[collection_name].count_documents({})
                print(f"   Documenti presenti: {doc_count}")
                
                # Ask for confirmation
                response = input(f"   Confermi eliminazione? (s/n): ")
                if response.lower() == 's':
                    db[collection_name].drop()
                    print(f"   ✓ Collezione eliminata\n")
                    removed_count += 1
                else:
                    print(f"   ⊘ Operazione annullata\n")
            else:
                print(f"ℹ️  Collezione '{collection_name}' non trovata (già rimossa?)\n")
        
        print(f"\n{'='*60}")
        print(f"✓ Pulizia completata: {removed_count} collezioni rimosse")
        print(f"{'='*60}\n")
        
        # Show remaining collections
        remaining = db.list_collection_names()
        print(f"📋 Collezioni rimanenti:")
        for coll in remaining:
            count = db[coll].count_documents({})
            print(f"   • {coll}: {count} documenti")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Errore: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Pulisci collezioni obsolete dal database MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter
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
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("PULIZIA DATABASE - Rimozione Collezioni Obsolete")
    print("="*60)
    print("\n⚠️  ATTENZIONE: Questa operazione eliminerà le seguenti collezioni:")
    print("   • clinical_data")
    print("   • decision_support")
    print("   • audit_logs")
    print("\nI dati in queste collezioni verranno persi definitivamente!")
    print("Assicurati di aver fatto un backup se necessario.\n")
    
    response = input("Vuoi continuare? (s/n): ")
    if response.lower() != 's':
        print("\n⊘ Operazione annullata dall'utente")
        sys.exit(0)
    
    cleanup_collections(args.connection, args.database)


if __name__ == "__main__":
    main()
