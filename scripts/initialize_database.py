"""
Script to initialize MongoDB database with schemas and indexes.

This script:
1. Creates all required collections with schema validation
2. Sets up indexes for optimal query performance
3. Validates the database structure

Run this script before using the EarlyCare Gateway with MongoDB.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.mongodb_repository import MongoDBPatientRepository
from src.database.schemas import get_collection_schemas, get_indexes
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database(connection_string: str = None, 
                       database_name: str = None,
    """
    Initialize MongoDB database with schemas and indexes.
    
    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database to initialize
    """
    print("=" * 70)
    print("EarlyCare Gateway - MongoDB Database Initialization")
    print("=" * 70)
    
    try:
        print(f"\n📊 Connecting to MongoDB...")
        print(f"   Connection: {connection_string}")
        print(f"   Database: {database_name}")
        
        # Initialize repository (this creates collections and indexes)
        db = MongoDBPatientRepository(
            connection_string=connection_string,
            database_name=database_name
        )
        
        print(f"\n✓ Successfully connected to MongoDB")
        
        # Verify collections
        print(f"\n📋 Verifying collections...")
        collections = db.db.list_collection_names()
        expected_collections = [
            'patients',
            'clinical_data',
            'patient_records',
            'decision_support',
            'audit_logs'
        ]
        
        for collection in expected_collections:
            if collection in collections:
                print(f"   ✓ {collection}")
                
                # Get collection stats
                stats = db.db.command("collstats", collection)
                print(f"      - Documents: {stats.get('count', 0)}")
                print(f"      - Indexes: {stats.get('nindexes', 0)}")
            else:
                print(f"   ✗ {collection} - NOT FOUND")
        
        # Display schema information
        print(f"\n📐 Schema Validation:")
        schemas = get_collection_schemas()
        for collection_name in expected_collections:
            if collection_name in schemas:
                schema = schemas[collection_name]
                level = schema.get('validationLevel', 'N/A')
                action = schema.get('validationAction', 'N/A')
                print(f"   {collection_name}:")
                print(f"      - Validation Level: {level}")
                print(f"      - Validation Action: {action}")
        
        # Display index information
        print(f"\n🔍 Indexes:")
        indexes_def = get_indexes()
        for collection_name, indexes in indexes_def.items():
            print(f"   {collection_name}: {len(indexes)} indexes")
            for idx in indexes:
                keys = idx["keys"]
                unique = " (UNIQUE)" if idx.get("unique", False) else ""
                print(f"      - {keys}{unique}")
        
        # Get current statistics
        print(f"\n📈 Current Database Statistics:")
        stats = db.get_statistics()
        print(f"   Total Patients: {stats.get('total_patients', 0)}")
        print(f"   Total Clinical Data: {stats.get('total_clinical_data', 0)}")
        print(f"   Total Patient Records: {stats.get('total_records', 0)}")
        print(f"   Total Decisions: {stats.get('total_decisions', 0)}")
        
        if stats.get('priority_counts'):
            print(f"\n   Priority Distribution:")
            for priority, count in stats['priority_counts'].items():
                print(f"      - {priority}: {count}")
        
        if stats.get('data_type_counts'):
            print(f"\n   Clinical Data Types:")
            for data_type, count in stats['data_type_counts'].items():
                print(f"      - {data_type}: {count}")
        
        print(f"\n{'=' * 70}")
        print("✅ Database initialization completed successfully!")
        print("=" * 70)
        print("\nYou can now use the EarlyCare Gateway with MongoDB.")
        print("Run: python examples/example_mongodb_usage.py")
        
        # Close connection
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error initializing database:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def drop_database(connection_string: str = "mongodb+srv://angelospeed2003:kjhwoP4rXR3UsnaV@mav.0zz64yh.mongodb.net/",
                 database_name: str = "earlycare"):
    """
    Drop the entire database (use with caution!).
    
    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database to drop
    """
    print(f"\n⚠️  WARNING: This will permanently delete the '{database_name}' database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("Operation cancelled.")
        return
    
    try:
        from pymongo import MongoClient
        client = MongoClient(connection_string)
        client.drop_database(database_name)
        print(f"✓ Database '{database_name}' has been dropped.")
        client.close()
    except Exception as e:
        print(f"✗ Error dropping database: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Initialize EarlyCare Gateway MongoDB database"
    )
    parser.add_argument(
        "--connection",
        default=Config.MONGODB_CONNECTION_STRING,
        help="MongoDB connection string (default: from .env)"
    )
    parser.add_argument(
        "--database",
        default="earlycare",
        help="Database name (default: earlycare)"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop the database before initialization (DANGEROUS!)"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        drop_database(args.connection, args.database)
        print()
    
    success = initialize_database(args.connection, args.database)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
