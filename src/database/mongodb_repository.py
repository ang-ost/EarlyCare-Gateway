"""MongoDB repository for patient data management."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure, CollectionInvalid
import logging
import ssl
import certifi

from ..models.patient import Patient, PatientRecord, Gender
from ..models.clinical_data import TextData, SignalData, ImageData, DataType, DataSource
from ..models.decision import DecisionSupport
from .schemas import get_collection_schemas, get_indexes


logger = logging.getLogger(__name__)


class MongoDBPatientRepository:
    """Repository for managing patient data in MongoDB."""
    
    def __init__(self, connection_string: str, database_name: str = "earlycare", **kwargs):
        """
        Initialize MongoDB repository.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database to use
            **kwargs: Additional connection parameters (tlsAllowInvalidCertificates, etc.)
        """
        try:
            # Default connection parameters for MongoDB Atlas
            connection_params = {
                'serverSelectionTimeoutMS': 10000,
                'connectTimeoutMS': 20000,
                'socketTimeoutMS': 20000,
            }
            
            # If using mongodb+srv (Atlas), add SSL/TLS parameters
            if 'mongodb+srv://' in connection_string or 'ssl=true' in connection_string.lower():
                # WORKAROUND for Python 3.14 SSL issues - disable strict verification
                connection_params.update({
                    'tls': True,
                    'tlsAllowInvalidCertificates': True,  # Disable certificate validation
                    'tlsAllowInvalidHostnames': True,      # Disable hostname validation
                })
                logger.warning("⚠️  Using relaxed SSL verification - NOT RECOMMENDED for production!")
                logger.warning("⚠️  Consider using Python 3.12 for proper SSL support")
            
            # Merge with user-provided kwargs (allows override)
            connection_params.update(kwargs)
            
            logger.info("Attempting MongoDB connection...")
            self.client = MongoClient(connection_string, **connection_params)
            self.db = self.client[database_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✓ MongoDB connection successful")
            
            # Collections
            self.patients_collection = self.db['patients']
            self.patient_records_collection = self.db['patient_records']
            self.doctors_collection = self.db['doctors']  # New: Collection for doctors
            self.audit_logs_collection = self.db['audit_logs']
            
            # Initialize collections with schemas
            self._initialize_collections()
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {database_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _initialize_collections(self):
        """Initialize collections with schema validation."""
        schemas = get_collection_schemas()
        
        for collection_name, schema in schemas.items():
            try:
                # Check if collection exists
                if collection_name not in self.db.list_collection_names():
                    # Create collection with schema validation
                    self.db.create_collection(collection_name, **schema)
                    logger.info(f"Created collection '{collection_name}' with schema validation")
                else:
                    # Update validation rules for existing collection
                    try:
                        self.db.command({
                            "collMod": collection_name,
                            "validator": schema["validator"],
                            "validationLevel": schema.get("validationLevel", "moderate"),
                            "validationAction": schema.get("validationAction", "warn")
                        })
                        logger.info(f"Updated schema validation for collection '{collection_name}'")
                    except Exception as e:
                        logger.warning(f"Could not update validation for '{collection_name}': {e}")
            except CollectionInvalid:
                logger.debug(f"Collection '{collection_name}' already exists")
            except Exception as e:
                logger.warning(f"Error initializing collection '{collection_name}': {e}")
    
    def _create_indexes(self):
        """Create indexes for better query performance."""
        indexes_def = get_indexes()
        
        for collection_name, indexes in indexes_def.items():
            collection = self.db[collection_name]
            for index_spec in indexes:
                try:
                    keys = index_spec["keys"]
                    unique = index_spec.get("unique", False)
                    collection.create_index(keys, unique=unique)
                except Exception as e:
                    logger.warning(f"Could not create index on {collection_name}: {e}")
    
    def _patient_to_dict(self, patient: Patient) -> Dict[str, Any]:
        """Convert Patient object to dictionary for MongoDB."""
        patient_dict = {
            "patient_id": patient.patient_id,
            "nome": patient.nome,
            "cognome": patient.cognome,
            "data_nascita": patient.data_nascita,
            "comune_nascita": patient.comune_nascita,
            "codice_fiscale": patient.codice_fiscale,
            "data_decesso": patient.data_decesso,
            "allergie": patient.allergie,
            "malattie_permanenti": patient.malattie_permanenti,
            "age": patient.age,
            "ethnicity": patient.ethnicity,
            "primary_language": patient.primary_language,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Aggiungi campi opzionali solo se presenti
        if patient.gender:
            patient_dict["gender"] = patient.gender.value
        if patient.medical_record_number:
            patient_dict["medical_record_number"] = patient.medical_record_number
            
        return patient_dict
    
    def _dict_to_patient(self, data: Dict[str, Any]) -> Patient:
        """Convert MongoDB dictionary to Patient object."""
        try:
            # Handle both old and new schema
            # Old schema used: date_of_birth, allergies, medical_history
            # New schema uses: data_nascita, allergie, malattie_permanenti, nome, cognome, comune_nascita
            
            data_nascita = data.get("data_nascita") or data.get("date_of_birth") or datetime.now()
            allergie = data.get("allergie") or data.get("allergies") or []
            malattie = data.get("malattie_permanenti") or data.get("medical_history") or []
            
            return Patient(
                patient_id=data.get("patient_id", data.get("codice_fiscale", "")),
                nome=data.get("nome", ""),
                cognome=data.get("cognome", ""),
                data_nascita=data_nascita,
                comune_nascita=data.get("comune_nascita", ""),
                codice_fiscale=data.get("codice_fiscale", ""),
                data_decesso=data.get("data_decesso"),
                allergie=allergie,
                malattie_permanenti=malattie,
                gender=Gender(data["gender"]) if "gender" in data else None,
                medical_record_number=data.get("medical_record_number", ""),
                age=data.get("age"),
                ethnicity=data.get("ethnicity"),
                primary_language=data.get("primary_language", "it")
            )
        except Exception as e:
            logger.error(f"Error converting dict to patient: {e}")
            logger.error(f"Data: {data}")
            raise
    
    def _patient_record_to_dict(self, record: PatientRecord) -> Dict[str, Any]:
        """Convert PatientRecord object to dictionary for MongoDB."""
        # Convert clinical data to embedded documents
        clinical_data_embedded = []
        for data in record.clinical_data:
            data_dict = self._clinical_data_to_dict(data)
            if data_dict:
                clinical_data_embedded.append(data_dict)
        
        return {
            "encounter_id": record.encounter_id,
            "patient_id": record.patient.patient_id,
            "patient": {
                "patient_id": record.patient.patient_id,
                "nome": record.patient.nome,
                "cognome": record.patient.cognome,
                "codice_fiscale": record.patient.codice_fiscale
            },
            "chief_complaint": record.chief_complaint,
            "current_medications": record.current_medications,
            "clinical_data": clinical_data_embedded,
            "encounter_timestamp": record.encounter_timestamp,
            "priority": record.priority,
            "metadata": record.metadata,
            "processing_context": record.metadata.get("processing_context", {}),
            "created_at": datetime.now()
        }
    
    def _clinical_data_to_dict(self, clinical_data) -> Optional[Dict[str, Any]]:
        """
        Convert clinical data to dictionary for embedding in patient_records.
        
        Args:
            clinical_data: ClinicalData object (TextData, SignalData, or ImageData)
            
        Returns:
            Dictionary representation of clinical data
        """
        try:
            data_dict = {
                "data_id": clinical_data.data_id,
                "patient_id": clinical_data.patient_id,
                "timestamp": clinical_data.timestamp,
                "source": clinical_data.source.value,
                "data_type": clinical_data.data_type.value,
                "quality_score": clinical_data.quality_score,
                "is_validated": clinical_data.is_validated,
                "metadata": clinical_data.metadata
            }
            
            # Add type-specific fields
            if isinstance(clinical_data, TextData):
                data_dict.update({
                    "text_content": clinical_data.text_content,
                    "language": clinical_data.language,
                    "document_type": clinical_data.document_type
                })
            elif isinstance(clinical_data, SignalData):
                data_dict.update({
                    "signal_values": clinical_data.signal_values,
                    "sampling_rate": clinical_data.sampling_rate,
                    "signal_type": clinical_data.signal_type,
                    "units": clinical_data.units,
                    "duration": clinical_data.duration
                })
            elif isinstance(clinical_data, ImageData):
                data_dict.update({
                    "image_path": clinical_data.image_path,
                    "image_format": clinical_data.image_format,
                    "modality": clinical_data.modality,
                    "dimensions": {
                        "width": clinical_data.dimensions[0] if len(clinical_data.dimensions) > 0 else 0,
                        "height": clinical_data.dimensions[1] if len(clinical_data.dimensions) > 1 else 0,
                        "depth": clinical_data.dimensions[2] if len(clinical_data.dimensions) > 2 else 0
                    },
                    "body_part": clinical_data.body_part,
                    "contrast_used": clinical_data.contrast_used
                })
            
            return data_dict
        except Exception as e:
            logger.error(f"Error converting clinical data: {e}")
            return None
    
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
            print(f"\n=== DEBUG SAVE PATIENT ===")
            print(f"Nome: {patient_dict.get('nome')}")
            print(f"Cognome: {patient_dict.get('cognome')}")
            print(f"Codice Fiscale: {patient_dict.get('codice_fiscale')}")
            print(f"Comune Nascita: {patient_dict.get('comune_nascita')}")
            print(f"Data Nascita: {patient_dict.get('data_nascita')}")
            print(f"Full dict keys: {patient_dict.keys()}")
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
        Retrieve a patient by ID or codice_fiscale.
        
        Args:
            patient_id: Patient identifier or codice fiscale
            
        Returns:
            Patient object or None if not found
        """
        try:
            # Try searching by codice_fiscale first (most common)
            data = self.patients_collection.find_one({"codice_fiscale": patient_id})
            if data:
                print(f"\n=== DEBUG GET PATIENT ===")
                print(f"Found by codice_fiscale: {patient_id}")
                print(f"Nome from DB: {data.get('nome')}")
                print(f"Cognome from DB: {data.get('cognome')}")
                print(f"Comune Nascita from DB: {data.get('comune_nascita')}")
                print(f"Data Nascita from DB: {data.get('data_nascita')}")
                print(f"DB keys: {data.keys()}")
                return self._dict_to_patient(data)
            
            # If not found, try by patient_id
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
    
    def find_patients_by_name(self, nome: str, cognome: str) -> List[Patient]:
        """
        Find patients by nome and cognome.
        
        Args:
            nome: Patient first name
            cognome: Patient last name
            
        Returns:
            List of matching Patient objects
        """
        try:
            query = {
                "nome": {"$regex": f"^{nome}$", "$options": "i"},
                "cognome": {"$regex": f"^{cognome}$", "$options": "i"}
            }
            cursor = self.patients_collection.find(query)
            patients = [self._dict_to_patient(data) for data in cursor]
            return patients
        except Exception as e:
            logger.error(f"Error finding patients by name: {e}")
            return []
    
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
    
    def find_by_fiscal_code(self, codice_fiscale: str) -> Optional[Dict[str, Any]]:
        """
        Find patient by fiscal code and return as dictionary.
        
        Args:
            codice_fiscale: Patient fiscal code
            
        Returns:
            Patient dictionary or None if not found
        """
        try:
            patient = self.get_patient(codice_fiscale)
            if patient:
                # Convert Patient object to dictionary
                patient_dict = {
                    'patient_id': patient.patient_id,
                    'nome': patient.nome,
                    'cognome': patient.cognome,
                    'codice_fiscale': patient.codice_fiscale,
                    'data_nascita': patient.data_nascita.strftime('%Y-%m-%d') if patient.data_nascita else None,
                    'sesso': patient.gender.value if patient.gender else None,
                    'luogo_nascita': patient.comune_nascita,
                    'indirizzo': getattr(patient, 'indirizzo', None),
                    'telefono': getattr(patient, 'telefono', None),
                    'email': getattr(patient, 'email', None),
                    'cartelle_cliniche': self.get_patient_clinical_records(codice_fiscale)
                }
                return patient_dict
            return None
        except Exception as e:
            logger.error(f"Error finding patient by fiscal code: {e}")
            return None
    
    def search_by_name(self, nome: str, cognome: str) -> List[Dict[str, Any]]:
        """
        Search patients by name and return as dictionaries.
        
        Args:
            nome: Patient first name
            cognome: Patient last name
            
        Returns:
            List of patient dictionaries
        """
        try:
            patients = self.find_patients_by_name(nome, cognome)
            return [
                {
                    'patient_id': p.patient_id,
                    'nome': p.nome,
                    'cognome': p.cognome,
                    'codice_fiscale': p.codice_fiscale,
                    'data_nascita': p.data_nascita.strftime('%Y-%m-%d') if p.data_nascita else None,
                    'sesso': p.gender.value if p.gender else None,
                    'luogo_nascita': p.comune_nascita
                }
                for p in patients
            ]
        except Exception as e:
            logger.error(f"Error searching patients by name: {e}")
            return []
    
    def get_patient_clinical_records(self, codice_fiscale: str) -> List[Dict[str, Any]]:
        """
        Get all clinical records for a patient.
        
        Args:
            codice_fiscale: Patient fiscal code
            
        Returns:
            List of clinical records
        """
        try:
            # Search in patient_records collection
            records = self.patient_records_collection.find(
                {"patient.codice_fiscale": codice_fiscale}
            ).sort("encounter_timestamp", -1)
            
            return [
                {
                    'encounter_id': r.get('encounter_id'),
                    'timestamp': r.get('encounter_timestamp'),
                    'chief_complaint': r.get('chief_complaint'),
                    'symptoms': r.get('metadata', {}).get('symptoms'),
                    'diagnosis': r.get('metadata', {}).get('diagnosis'),
                    'treatment': r.get('metadata', {}).get('treatment'),
                    'notes': r.get('metadata', {}).get('notes'),
                    'vital_signs': r.get('metadata', {}).get('vital_signs', {}),
                    'priority': r.get('priority')
                }
                for r in records
            ]
        except Exception as e:
            logger.error(f"Error getting patient records: {e}")
            return []
    
    def add_clinical_record(self, codice_fiscale: str, record: Dict[str, Any]) -> bool:
        """
        Add a clinical record to a patient.
        
        Args:
            codice_fiscale: Patient fiscal code
            record: Clinical record data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            patient = self.get_patient(codice_fiscale)
            if not patient:
                logger.error(f"Patient not found: {codice_fiscale}")
                return False
            
            # Create patient record document
            record_doc = {
                'encounter_id': f"ENC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'patient': {
                    'patient_id': patient.patient_id,
                    'nome': patient.nome,
                    'cognome': patient.cognome,
                    'codice_fiscale': patient.codice_fiscale
                },
                'chief_complaint': record.get('chief_complaint'),
                'encounter_timestamp': datetime.now(),
                'priority': 'routine',
                'metadata': {
                    'symptoms': record.get('symptoms'),
                    'diagnosis': record.get('diagnosis'),
                    'treatment': record.get('treatment'),
                    'notes': record.get('notes'),
                    'vital_signs': record.get('vital_signs', {}),
                    'lab_results': record.get('lab_results', []),
                    'imaging': record.get('imaging', [])
                },
                'created_at': datetime.now()
            }
            
            self.patient_records_collection.insert_one(record_doc)
            logger.info(f"Added clinical record for patient: {codice_fiscale}")
            return True
        except Exception as e:
            logger.error(f"Error adding clinical record: {e}")
            return False
    
    def delete_clinical_records(self, codice_fiscale: str, indexes: List[int]) -> bool:
        """
        Delete multiple clinical records from a patient by their indexes.
        
        Args:
            codice_fiscale: Patient fiscal code
            indexes: List of record indexes to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all records for this patient (sorted by timestamp descending)
            records = list(self.patient_records_collection.find(
                {"patient.codice_fiscale": codice_fiscale}
            ).sort("encounter_timestamp", -1))
            
            if not records:
                logger.warning(f"No clinical records found for patient: {codice_fiscale}")
                return False
            
            # Validate indexes
            for idx in indexes:
                if idx < 0 or idx >= len(records):
                    logger.error(f"Invalid index {idx} for patient {codice_fiscale}")
                    return False
            
            # Get encounter_ids for the records to delete
            encounter_ids_to_delete = [records[idx]['encounter_id'] for idx in indexes]
            
            # Delete records from collection
            result = self.patient_records_collection.delete_many(
                {'encounter_id': {'$in': encounter_ids_to_delete}}
            )
            
            if result.deleted_count > 0:
                logger.info(f"Deleted {result.deleted_count} clinical record(s) for patient: {codice_fiscale}")
                return True
            else:
                logger.warning(f"No records were deleted for patient: {codice_fiscale}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting clinical records: {e}")
            return False
    
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
                "total_clinical_data": self.clinical_data_collection.count_documents({}),
                "total_decisions": self.decision_support_collection.count_documents({}),
                "priority_counts": {
                    "emergency": self.patient_records_collection.count_documents({"priority": "emergency"}),
                    "urgent": self.patient_records_collection.count_documents({"priority": "urgent"}),
                    "soon": self.patient_records_collection.count_documents({"priority": "soon"}),
                    "routine": self.patient_records_collection.count_documents({"priority": "routine"})
                },
                "data_type_counts": {
                    "text": self.clinical_data_collection.count_documents({"data_type": "text"}),
                    "signal": self.clinical_data_collection.count_documents({"data_type": "signal"}),
                    "image": self.clinical_data_collection.count_documents({"data_type": "image"})
                }
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    # Clinical Data operations
    
    def get_clinical_data(self, data_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve clinical data by ID.
        
        Args:
            data_id: Clinical data identifier
            
        Returns:
            Clinical data dictionary or None if not found
        """
        try:
            return self.clinical_data_collection.find_one({"data_id": data_id})
        except Exception as e:
            logger.error(f"Error retrieving clinical data: {e}")
            return None
    
    def get_patient_clinical_data(
        self, 
        patient_id: str, 
        data_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all clinical data for a patient.
        
        Args:
            patient_id: Patient identifier
            data_type: Optional filter by data type (text, signal, image)
            limit: Maximum number of records to return
            
        Returns:
            List of clinical data dictionaries
        """
        try:
            query = {"patient_id": patient_id}
            if data_type:
                query["data_type"] = data_type
            
            cursor = self.clinical_data_collection.find(query).sort(
                "timestamp", DESCENDING
            ).limit(limit)
            
            return list(cursor)
        except Exception as e:
            logger.error(f"Error retrieving patient clinical data: {e}")
            return []
    
    def delete_clinical_data(self, data_id: str) -> bool:
        """
        Delete clinical data.
        
        Args:
            data_id: Clinical data identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.clinical_data_collection.delete_one({"data_id": data_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted clinical data: {data_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting clinical data: {e}")
            return False
    
    # Decision Support operations
    
    def save_decision_support(self, decision: DecisionSupport, encounter_id: str) -> bool:
        """
        Save decision support results.
        
        Args:
            decision: DecisionSupport object
            encounter_id: Associated encounter ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            decision_dict = {
                "request_id": decision.request_id,
                "patient_id": decision.patient_id,
                "encounter_id": encounter_id,
                "timestamp": decision.timestamp,
                "diagnoses": [
                    {
                        "condition": d.condition,
                        "icd_code": d.icd_code,
                        "confidence_score": d.confidence_score,
                        "confidence_level": d.confidence_level.value,
                        "evidence": d.evidence,
                        "risk_factors": d.risk_factors,
                        "differential_diagnoses": d.differential_diagnoses,
                        "recommended_tests": d.recommended_tests,
                        "recommended_specialists": d.recommended_specialists
                    }
                    for d in decision.diagnoses
                ],
                "urgency_level": decision.urgency_level.value,
                "triage_score": decision.triage_score,
                "alerts": decision.alerts,
                "warnings": decision.warnings,
                "clinical_notes": decision.clinical_notes,
                "models_used": decision.models_used,
                "processing_time_ms": decision.processing_time_ms,
                "explanation": decision.explanation,
                "feature_importance": decision.feature_importance,
                "metadata": decision.metadata,
                "created_at": datetime.now()
            }
            
            self.decision_support_collection.insert_one(decision_dict)
            logger.info(f"Saved decision support: {decision.request_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving decision support: {e}")
            return False
    
    def get_decision_support(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve decision support by request ID.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Decision support dictionary or None if not found
        """
        try:
            return self.decision_support_collection.find_one({"request_id": request_id})
        except Exception as e:
            logger.error(f"Error retrieving decision support: {e}")
            return None
    
    def get_patient_decisions(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get decision support results for a patient.
        
        Args:
            patient_id: Patient identifier
            limit: Maximum number of records to return
            
        Returns:
            List of decision support dictionaries
        """
        try:
            cursor = self.decision_support_collection.find(
                {"patient_id": patient_id}
            ).sort("timestamp", DESCENDING).limit(limit)
            
            return list(cursor)
        except Exception as e:
            logger.error(f"Error retrieving patient decisions: {e}")
            return []
    
    def get_decisions_by_urgency(self, urgency_level: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Find decision support results by urgency level.
        
        Args:
            urgency_level: Urgency level (routine, soon, urgent, emergency)
            limit: Maximum number of records to return
            
        Returns:
            List of decision support dictionaries
        """
        try:
            cursor = self.decision_support_collection.find(
                {"urgency_level": urgency_level}
            ).sort("timestamp", DESCENDING).limit(limit)
            
            return list(cursor)
        except Exception as e:
            logger.error(f"Error finding decisions by urgency: {e}")
            return []
    
    # Audit logging
    
    def log_audit_event(
        self,
        event_type: str,
        user_id: str,
        action: str,
        patient_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (access, create, update, delete, etc.)
            user_id: User performing the action
            action: Description of the action
            patient_id: Optional patient ID
            resource_type: Type of resource affected
            resource_id: ID of affected resource
            success: Whether the action succeeded
            error_message: Error message if failed
            metadata: Additional metadata
            
        Returns:
            True if logged successfully
        """
        try:
            event_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            audit_dict = {
                "event_id": event_id,
                "timestamp": datetime.now(),
                "event_type": event_type,
                "user_id": user_id,
                "patient_id": patient_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
                "success": success,
                "error_message": error_message,
                "metadata": metadata or {}
            }
            
            self.audit_logs_collection.insert_one(audit_dict)
            return True
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            return False
    
    def get_audit_logs(
        self,
        patient_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs with optional filters.
        
        Args:
            patient_id: Filter by patient ID
            user_id: Filter by user ID
            event_type: Filter by event type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of records
            
        Returns:
            List of audit log dictionaries
        """
        try:
            query = {}
            
            if patient_id:
                query["patient_id"] = patient_id
            if user_id:
                query["user_id"] = user_id
            if event_type:
                query["event_type"] = event_type
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["timestamp"] = date_query
            
            cursor = self.audit_logs_collection.find(query).sort(
                "timestamp", DESCENDING
            ).limit(limit)
            
            return list(cursor)
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []
    
    # ========== DOCTOR MANAGEMENT ==========
    
    def save_doctor(self, doctor) -> bool:
        """
        Save a new doctor to the database.
        
        Args:
            doctor: Doctor object with doctor_id, nome, cognome, etc.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if doctor already exists
            existing = self.doctors_collection.find_one({'doctor_id': doctor.doctor_id})
            if existing:
                logger.warning(f"Doctor with ID {doctor.doctor_id} already exists")
                return False
            
            # Convert to dict and insert
            doctor_dict = {
                'doctor_id': doctor.doctor_id,
                'nome': doctor.nome,
                'cognome': doctor.cognome,
                'specializzazione': doctor.specializzazione,
                'ospedale_affiliato': doctor.ospedale_affiliato,
                'password_hash': doctor.password_hash,
                'created_at': doctor.created_at,
                'last_login': doctor.last_login,
                'is_active': doctor.is_active
            }
            
            result = self.doctors_collection.insert_one(doctor_dict)
            logger.info(f"Doctor {doctor.doctor_id} saved successfully")
            return True
            
        except DuplicateKeyError:
            logger.error(f"Doctor with ID {doctor.doctor_id} already exists")
            return False
        except Exception as e:
            logger.error(f"Error saving doctor: {e}")
            return False
    
    def find_doctor_by_id(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a doctor by doctor_id.
        
        Args:
            doctor_id: The doctor's unique ID
            
        Returns:
            Dictionary with doctor data or None if not found
        """
        try:
            doctor = self.doctors_collection.find_one({'doctor_id': doctor_id})
            if doctor:
                doctor.pop('_id', None)  # Remove MongoDB's _id field
            return doctor
        except Exception as e:
            logger.error(f"Error finding doctor: {e}")
            return None
    
    def verify_doctor_login(self, doctor_id: str, password: str) -> bool:
        """
        Verify doctor login credentials.
        
        Args:
            doctor_id: Doctor's unique ID
            password: Plain text password to verify
            
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            doctor_data = self.find_doctor_by_id(doctor_id)
            
            if not doctor_data:
                logger.warning(f"Doctor {doctor_id} not found")
                return False
            
            if not doctor_data.get('is_active', True):
                logger.warning(f"Doctor {doctor_id} is not active")
                return False
            
            # Verify password
            from ..models.doctor import Doctor
            password_valid = Doctor.verify_password(password, doctor_data['password_hash'])
            
            if password_valid:
                # Update last_login timestamp
                self.doctors_collection.update_one(
                    {'doctor_id': doctor_id},
                    {'$set': {'last_login': datetime.now()}}
                )
                logger.info(f"Doctor {doctor_id} logged in successfully")
                return True
            else:
                logger.warning(f"Invalid password for doctor {doctor_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying doctor login: {e}")
            return False
    
    def doctor_id_exists(self, doctor_id: str) -> bool:
        """
        Check if a doctor ID already exists.
        
        Args:
            doctor_id: The doctor ID to check
            
        Returns:
            True if doctor exists, False otherwise
        """
        try:
            return self.doctors_collection.find_one({'doctor_id': doctor_id}) is not None
        except Exception as e:
            logger.error(f"Error checking doctor ID: {e}")
            return False

    def delete_doctor_by_id(self, doctor_id: str) -> bool:
        """
        Delete a doctor by their ID.
        
        Args:
            doctor_id: The doctor ID to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = self.doctors_collection.delete_one({'doctor_id': doctor_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting doctor: {e}")
            return False

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
