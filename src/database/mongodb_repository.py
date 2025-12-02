"""MongoDB repository for patient data management."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
import logging

from ..models.patient import Patient, PatientRecord, Gender


logger = logging.getLogger(__name__)


class MongoDBPatientRepository:
    """Repository for managing patient data in MongoDB."""
    
    def __init__(self, connection_string: str, database_name: str = "earlycare"):
        """
        Initialize MongoDB repository.
        
        Args:
            connection_string: MongoDB connection string (e.g., 'mongodb://localhost:27017/')
            database_name: Name of the database to use
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            
            # Collections
            self.patients_collection = self.db['patients']
            self.patient_records_collection = self.db['patient_records']
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {database_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes for better query performance."""
        # Patient indexes
        self.patients_collection.create_index([("patient_id", ASCENDING)], unique=True)
        self.patients_collection.create_index([("medical_record_number", ASCENDING)])
        self.patients_collection.create_index([("date_of_birth", ASCENDING)])
        
        # Patient records indexes
        self.patient_records_collection.create_index([("encounter_id", ASCENDING)], unique=True)
        self.patient_records_collection.create_index([("patient.patient_id", ASCENDING)])
        self.patient_records_collection.create_index([("encounter_timestamp", DESCENDING)])
        self.patient_records_collection.create_index([("priority", ASCENDING)])
    
    def _patient_to_dict(self, patient: Patient) -> Dict[str, Any]:
        """Convert Patient object to dictionary for MongoDB."""
        return {
            "patient_id": patient.patient_id,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender.value,
            "medical_record_number": patient.medical_record_number,
            "age": patient.age,
            "ethnicity": patient.ethnicity,
            "primary_language": patient.primary_language,
            "chief_complaint": patient.chief_complaint,
            "medical_history": patient.medical_history,
            "current_medications": patient.current_medications,
            "allergies": patient.allergies,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    
    def _dict_to_patient(self, data: Dict[str, Any]) -> Patient:
        """Convert MongoDB dictionary to Patient object."""
        return Patient(
            patient_id=data["patient_id"],
            date_of_birth=data["date_of_birth"],
            gender=Gender(data["gender"]),
            medical_record_number=data["medical_record_number"],
            age=data.get("age"),
            ethnicity=data.get("ethnicity"),
            primary_language=data.get("primary_language", "en"),
            chief_complaint=data.get("chief_complaint"),
            medical_history=data.get("medical_history", []),
            current_medications=data.get("current_medications", []),
            allergies=data.get("allergies", [])
        )
    
    def _patient_record_to_dict(self, record: PatientRecord) -> Dict[str, Any]:
        """Convert PatientRecord object to dictionary for MongoDB."""
        return {
            "encounter_id": record.encounter_id,
            "patient": self._patient_to_dict(record.patient),
            "clinical_data": [
                {
                    "data_type": data.data_type.value,
                    "timestamp": data.timestamp,
                    "values": data.values,
                    "unit": data.unit,
                    "source": data.source,
                    "quality_score": data.quality_score,
                    "metadata": data.metadata
                }
                for data in record.clinical_data
            ],
            "encounter_timestamp": record.encounter_timestamp,
            "priority": record.priority,
            "metadata": record.metadata,
            "created_at": datetime.now()
        }
    
    # Patient CRUD operations
    
    def save_patient(self, patient: Patient) -> bool:
        """
        Save a new patient to the database.
        
        Args:
            patient: Patient object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            patient_dict = self._patient_to_dict(patient)
            self.patients_collection.insert_one(patient_dict)
            logger.info(f"Saved patient: {patient.patient_id}")
            return True
        except DuplicateKeyError:
            logger.warning(f"Patient {patient.patient_id} already exists")
            return False
        except Exception as e:
            logger.error(f"Error saving patient: {e}")
            return False
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """
        Retrieve a patient by ID.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient object or None if not found
        """
        try:
            data = self.patients_collection.find_one({"patient_id": patient_id})
            if data:
                return self._dict_to_patient(data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving patient: {e}")
            return None
    
    def update_patient(self, patient: Patient) -> bool:
        """
        Update an existing patient.
        
        Args:
            patient: Patient object with updated information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            patient_dict = self._patient_to_dict(patient)
            patient_dict["updated_at"] = datetime.now()
            
            result = self.patients_collection.update_one(
                {"patient_id": patient.patient_id},
                {"$set": patient_dict}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated patient: {patient.patient_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating patient: {e}")
            return False
    
    def delete_patient(self, patient_id: str) -> bool:
        """
        Delete a patient from the database.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.patients_collection.delete_one({"patient_id": patient_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted patient: {patient_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting patient: {e}")
            return False
    
    def find_patients(self, query: Dict[str, Any]) -> List[Patient]:
        """
        Find patients matching a query.
        
        Args:
            query: MongoDB query dictionary
            
        Returns:
            List of matching Patient objects
        """
        try:
            cursor = self.patients_collection.find(query)
            return [self._dict_to_patient(data) for data in cursor]
        except Exception as e:
            logger.error(f"Error finding patients: {e}")
            return []
    
    # Patient Record operations
    
    def save_patient_record(self, record: PatientRecord) -> bool:
        """
        Save a patient record to the database.
        
        Args:
            record: PatientRecord object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            record_dict = self._patient_record_to_dict(record)
            self.patient_records_collection.insert_one(record_dict)
            logger.info(f"Saved patient record: {record.encounter_id}")
            return True
        except DuplicateKeyError:
            logger.warning(f"Patient record {record.encounter_id} already exists")
            return False
        except Exception as e:
            logger.error(f"Error saving patient record: {e}")
            return False
    
    def get_patient_records(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve patient records for a specific patient.
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of records to return
            
        Returns:
            List of patient record dictionaries
        """
        try:
            cursor = self.patient_records_collection.find(
                {"patient.patient_id": patient_id}
            ).sort("encounter_timestamp", DESCENDING).limit(limit)
            
            return list(cursor)
        except Exception as e:
            logger.error(f"Error retrieving patient records: {e}")
            return []
    
    def get_record_by_encounter(self, encounter_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific patient record by encounter ID.
        
        Args:
            encounter_id: Encounter identifier
            
        Returns:
            Patient record dictionary or None if not found
        """
        try:
            return self.patient_records_collection.find_one({"encounter_id": encounter_id})
        except Exception as e:
            logger.error(f"Error retrieving encounter record: {e}")
            return None
    
    def find_records_by_priority(self, priority: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Find patient records by priority level.
        
        Args:
            priority: Priority level (routine, urgent, emergency)
            limit: Maximum number of records to return
            
        Returns:
            List of patient record dictionaries
        """
        try:
            cursor = self.patient_records_collection.find(
                {"priority": priority}
            ).sort("encounter_timestamp", DESCENDING).limit(limit)
            
            return list(cursor)
        except Exception as e:
            logger.error(f"Error finding records by priority: {e}")
            return []
    
    def get_recent_records(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent patient records within specified hours.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of records to return
            
        Returns:
            List of patient record dictionaries
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cursor = self.patient_records_collection.find(
                {"encounter_timestamp": {"$gte": cutoff_time}}
            ).sort("encounter_timestamp", DESCENDING).limit(limit)
            
            return list(cursor)
        except Exception as e:
            logger.error(f"Error retrieving recent records: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            return {
                "total_patients": self.patients_collection.count_documents({}),
                "total_records": self.patient_records_collection.count_documents({}),
                "priority_counts": {
                    "emergency": self.patient_records_collection.count_documents({"priority": "emergency"}),
                    "urgent": self.patient_records_collection.count_documents({"priority": "urgent"}),
                    "routine": self.patient_records_collection.count_documents({"priority": "routine"})
                }
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
