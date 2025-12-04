"""
Script to clean up extra collections from MongoDB database.
Keeps only 'patients' and 'patient_records' collections.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pymongo import MongoClient
import yaml


def load_config():
    """Load database configuration."""
    config_path = Path(__file__).parent.parent / "config" / "gateway_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def cleanup_collections():
    """Remove all collections except patients and patient_records."""
    print("🧹 Cleanup Extra Collections from MongoDB\n")
    
    # Load configuration
    config = load_config()
    db_config = config.get('database', {}).get('mongodb', {})
    connection_string = db_config.get('connection_string')
    database_name = db_config.get('database_name', 'earlycare')
    
    if not connection_string:
        print("❌ No connection string found in configuration")
        return
    
    print(f"📦 Connecting to database: {database_name}")
    
    try:
        # Connect to MongoDB with relaxed SSL for Python 3.14
        client = MongoClient(
            connection_string,
            tls=True,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=10000
        )
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB\n")
        
        db = client[database_name]
        
        # Get all collections
        all_collections = db.list_collection_names()
        print(f"📋 Found {len(all_collections)} collections:")
        for col in all_collections:
            print(f"   - {col}")
        
        # Collections to keep
        keep_collections = ['patients', 'patient_records']
        
        # Collections to drop
        drop_collections = [col for col in all_collections if col not in keep_collections]
        
        if not drop_collections:
            print("\n✅ No extra collections to remove. Database is already clean!")
            return
        
        print(f"\n🗑️  Collections to remove: {len(drop_collections)}")
        for col in drop_collections:
            print(f"   - {col}")
        
        # Ask for confirmation
        response = input("\n⚠️  Are you sure you want to drop these collections? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            print("\n🗑️  Dropping collections...")
            for col in drop_collections:
                try:
                    db.drop_collection(col)
                    print(f"   ✓ Dropped: {col}")
                except Exception as e:
                    print(f"   ✗ Error dropping {col}: {e}")
            
            # Verify remaining collections
            remaining_collections = db.list_collection_names()
            print(f"\n✅ Cleanup complete!")
            print(f"📋 Remaining collections: {remaining_collections}")
        else:
            print("\n❌ Operation cancelled")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    cleanup_collections()
