#!/usr/bin/env python3
"""
Script to delete doctors from MongoDB database.
Usage:
  python delete_doctors.py                    # Interactive mode
  python delete_doctors.py --list             # List all doctors
  python delete_doctors.py --delete <doctor_id>  # Delete specific doctor
  python delete_doctors.py --delete-all       # Delete all doctors
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.database.mongodb_repository import MongoDBPatientRepository


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_doctors(repo, doctors):
    """Print a formatted list of doctors"""
    if not doctors:
        print("No doctors found.")
        return
    
    print(f"\n{'Doctor ID':<20} {'Nome':<15} {'Cognome':<15} {'Created':<20}")
    print("-" * 70)
    for doc in doctors:
        created = doc.get('created_at', 'N/A')
        if hasattr(created, 'strftime'):
            created = created.strftime('%Y-%m-%d %H:%M:%S')
        print(f"{doc['doctor_id']:<20} {doc['nome']:<15} {doc['cognome']:<15} {created:<20}")


def view_all_doctors(repo):
    """View all doctors in database"""
    print_header("VIEW ALL DOCTORS")
    
    try:
        doctors = repo.db['doctors'].find({})
        doctor_list = list(doctors)
        
        if not doctor_list:
            print("No doctors found in database.")
            return doctor_list
        
        print(f"\nTotal doctors: {len(doctor_list)}\n")
        print_doctors(repo, doctor_list)
        return doctor_list
    except Exception as e:
        print(f"❌ Error retrieving doctors: {e}")
        return []


def delete_specific_doctor(repo, doctor_id):
    """Delete a specific doctor by ID"""
    print_header(f"DELETE DOCTOR: {doctor_id}")
    
    try:
        # Check if doctor exists
        doctor = repo.find_doctor_by_id(doctor_id)
        if not doctor:
            print(f"❌ Doctor '{doctor_id}' not found.")
            return False
        
        # Show doctor details before deletion
        print(f"\nDoctor to delete:")
        print(f"  ID: {doctor['doctor_id']}")
        print(f"  Name: {doctor['nome']} {doctor['cognome']}")
        print(f"  Created: {doctor.get('created_at', 'N/A')}")
        
        # Confirm deletion
        confirm = input("\n⚠️  Are you sure you want to delete this doctor? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Deletion cancelled.")
            return False
        
        # Delete the doctor
        result = repo.db['doctors'].delete_one({'doctor_id': doctor_id})
        
        if result.deleted_count > 0:
            print(f"✅ Doctor '{doctor_id}' successfully deleted!")
            return True
        else:
            print(f"❌ Failed to delete doctor '{doctor_id}'.")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting doctor: {e}")
        return False


def delete_all_doctors(repo):
    """Delete all doctors from database"""
    print_header("DELETE ALL DOCTORS")
    
    try:
        doctors = repo.db['doctors'].find({})
        doctor_list = list(doctors)
        
        if not doctor_list:
            print("No doctors found to delete.")
            return False
        
        print(f"\nFound {len(doctor_list)} doctor(s) to delete:\n")
        print_doctors(repo, doctor_list)
        
        # Confirm deletion
        confirm = input("\n⚠️  Are you sure you want to delete ALL doctors? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Deletion cancelled.")
            return False
        
        # Double confirmation for safety
        confirm2 = input("⚠️  This action cannot be undone. Type 'DELETE ALL' to confirm: ").strip()
        if confirm2 != 'DELETE ALL':
            print("❌ Deletion cancelled.")
            return False
        
        # Delete all doctors
        result = repo.db['doctors'].delete_many({})
        
        print(f"\n✅ Successfully deleted {result.deleted_count} doctor(s)!")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting doctors: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Delete doctors from MongoDB database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python delete_doctors.py                      # Interactive menu
  python delete_doctors.py --list               # List all doctors
  python delete_doctors.py --delete MR1733A7K9  # Delete specific doctor
  python delete_doctors.py --delete-all         # Delete all doctors
        """
    )
    parser.add_argument('--list', action='store_true', 
                        help='List all doctors in database')
    parser.add_argument('--delete', metavar='DOCTOR_ID', 
                        help='Delete specific doctor by ID')
    parser.add_argument('--delete-all', action='store_true', 
                        help='Delete all doctors from database')
    
    args = parser.parse_args()
    
    try:
        # Initialize configuration
        config = Config()
        
        # Create repository with connection string and database name
        repo = MongoDBPatientRepository(
            connection_string=config.MONGODB_CONNECTION_STRING,
            database_name=config.MONGODB_DATABASE_NAME
        )
        
        print("✅ Connected to MongoDB successfully!")
        
        # Handle arguments
        if args.list:
            view_all_doctors(repo)
        
        elif args.delete:
            delete_specific_doctor(repo, args.delete)
        
        elif args.delete_all:
            delete_all_doctors(repo)
        
        else:
            # Interactive mode
            interactive_menu(repo)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def interactive_menu(repo):
    """Interactive menu mode"""
    print_header("DOCTOR MANAGEMENT - DELETE DOCTORS")
    
    while True:
        print("""
Options:
  1. View all doctors
  2. Delete specific doctor
  3. Delete all doctors
  4. Exit
        """)
        choice = input("Select option (1-4): ").strip()
        
        if choice == '1':
            view_all_doctors(repo)
        
        elif choice == '2':
            doctor_id = input("\nEnter doctor ID to delete: ").strip()
            if doctor_id:
                delete_specific_doctor(repo, doctor_id)
            else:
                print("❌ Invalid doctor ID.")
        
        elif choice == '3':
            delete_all_doctors(repo)
        
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == '__main__':
    main()
