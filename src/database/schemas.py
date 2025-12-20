"""
MongoDB Schema Definitions for EarlyCare Gateway

This module defines the schema structure for storing patient data and clinical records in MongoDB.
Only two collections: patients and patient_records.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


class MongoDBSchemas:
    """MongoDB collection schemas for EarlyCare Gateway."""
    
    # =================================================================
    # PATIENTS COLLECTION SCHEMA
    # =================================================================
    
    PATIENTS_SCHEMA = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["patient_id", "nome", "cognome", "data_nascita", "comune_nascita", "codice_fiscale"],
                "properties": {
                    "_id": {
                        "bsonType": "objectId",
                        "description": "MongoDB unique identifier"
                    },
                    "patient_id": {
                        "bsonType": "string",
                        "description": "Unique patient identifier (required, indexed)"
                    },
                    "nome": {
                        "bsonType": "string",
                        "description": "Nome del paziente (required)"
                    },
                    "cognome": {
                        "bsonType": "string",
                        "description": "Cognome del paziente (required)"
                    },
                    "data_nascita": {
                        "bsonType": "date",
                        "description": "Data di nascita del paziente (required)"
                    },
                    "data_decesso": {
                        "bsonType": ["date", "null"],
                        "description": "Data del decesso del paziente (optional)"
                    },
                    "comune_nascita": {
                        "bsonType": "string",
                        "description": "Comune di nascita del paziente (required)"
                    },
                    "codice_fiscale": {
                        "bsonType": "string",
                        "description": "Codice fiscale del paziente (required, indexed)"
                    },
                    "allergie": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        },
                        "description": "Lista delle allergie del paziente"
                    },
                    "malattie_permanenti": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        },
                        "description": "Lista delle malattie permanenti (es. diabete, celiachia, malattie cardiovascolari, malattie neurodegenerative)"
                    },
                    "gender": {
                        "enum": ["male", "female", "other", "unknown"],
                        "description": "Patient gender"
                    },
                    "medical_record_number": {
                        "bsonType": "string",
                        "description": "Medical record number (indexed)"
                    },
                    "age": {
                        "bsonType": ["int", "null"],
                        "minimum": 0,
                        "maximum": 150,
                        "description": "Calculated age in years"
                    },
                    "ethnicity": {
                        "bsonType": ["string", "null"],
                        "description": "Patient ethnicity"
                    },
                    "primary_language": {
                        "bsonType": "string",
                        "description": "Primary language code (default: 'it')"
                    },
                    "created_at": {
                        "bsonType": "date",
                        "description": "Record creation timestamp"
                    },
                    "updated_at": {
                        "bsonType": "date",
                        "description": "Last update timestamp"
                    }
                }
            }
        },
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
    
    # =================================================================
    # PATIENT RECORDS COLLECTION SCHEMA
    # =================================================================
    
    PATIENT_RECORDS_SCHEMA = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["encounter_id", "patient_id", "encounter_timestamp", "priority"],
                "properties": {
                    "_id": {
                        "bsonType": "objectId"
                    },
                    "encounter_id": {
                        "bsonType": "string",
                        "description": "Unique encounter identifier (required, indexed)"
                    },
                    "patient_id": {
                        "bsonType": "string",
                        "description": "Patient identifier (required, indexed)"
                    },
                    "patient": {
                        "bsonType": "object",
                        "description": "Reference to patient information",
                        "properties": {
                            "patient_id": {"bsonType": "string"},
                            "nome": {"bsonType": "string"},
                            "cognome": {"bsonType": "string"},
                            "codice_fiscale": {"bsonType": "string"}
                        }
                    },
                    "chief_complaint": {
                        "bsonType": ["string", "null"],
                        "description": "Primary reason for this visit/consultation"
                    },
                    "current_medications": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        },
                        "description": "Current medications at time of visit"
                    },
                    "clinical_data": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "data_id": {"bsonType": "string"},
                                "patient_id": {"bsonType": "string"},
                                "timestamp": {"bsonType": "date"},
                                "source": {"enum": ["electronic_health_record", "laboratory", "imaging", "wearable_device", "manual_entry"]},
                                "data_type": {"enum": ["text", "signal", "image"]},
                                "text_content": {"bsonType": ["string", "null"]},
                                "language": {"bsonType": ["string", "null"]},
                                "document_type": {"bsonType": ["string", "null"]},
                                "signal_values": {"bsonType": ["array", "null"]},
                                "sampling_rate": {"bsonType": ["double", "null"]},
                                "signal_type": {"bsonType": ["string", "null"]},
                                "units": {"bsonType": ["string", "null"]},
                                "duration": {"bsonType": ["double", "null"]},
                                "image_path": {"bsonType": ["string", "null"]},
                                "image_format": {"bsonType": ["string", "null"]},
                                "modality": {"bsonType": ["string", "null"]},
                                "dimensions": {"bsonType": ["object", "null"]},
                                "body_part": {"bsonType": ["string", "null"]},
                                "contrast_used": {"bsonType": ["bool", "null"]},
                                "quality_score": {"bsonType": ["double", "null"]},
                                "is_validated": {"bsonType": ["bool", "null"]},
                                "metadata": {"bsonType": ["object", "null"]}
                            }
                        },
                        "description": "Array of embedded clinical data for this specific encounter"
                    },
                    "encounter_timestamp": {
                        "bsonType": "date",
                        "description": "Encounter date/time (required, indexed)"
                    },
                    "priority": {
                        "enum": ["routine", "soon", "urgent", "emergency"],
                        "description": "Clinical priority level (required, indexed)"
                    },
                    "vital_signs": {
                        "bsonType": ["object", "null"],
                        "description": "Vital signs at time of encounter",
                        "properties": {
                            "blood_pressure": {"bsonType": ["string", "null"]},
                            "heart_rate": {"bsonType": ["string", "null"]},
                            "temperature": {"bsonType": ["string", "null"]},
                            "respiratory_rate": {"bsonType": ["string", "null"]},
                            "spo2": {"bsonType": ["string", "null"]}
                        }
                    },
                    "diagnosis": {
                        "bsonType": ["string", "null"],
                        "description": "Diagnosis for this encounter"
                    },
                    "treatment_plan": {
                        "bsonType": ["string", "null"],
                        "description": "Treatment plan for this encounter"
                    },
                    "notes": {
                        "bsonType": ["string", "null"],
                        "description": "Clinical notes for this encounter"
                    },
                    "metadata": {
                        "bsonType": "object",
                        "description": "Additional encounter metadata"
                    },
                    "processing_context": {
                        "bsonType": "object",
                        "description": "Context from processing pipeline",
                        "properties": {
                            "validation": {
                                "bsonType": "object",
                                "properties": {
                                    "is_valid": {"bsonType": "bool"},
                                    "errors": {"bsonType": "array"},
                                    "warnings": {"bsonType": "array"}
                                }
                            },
                            "enrichment": {
                                "bsonType": "object",
                                "properties": {
                                    "age_calculated": {"bsonType": ["bool", "null"]},
                                    "processing_timestamp": {"bsonType": ["string", "null"]},
                                    "data_count": {"bsonType": ["int", "null"]},
                                    "average_data_quality": {"bsonType": ["double", "null"]},
                                    "has_text_data": {"bsonType": ["bool", "null"]},
                                    "has_signal_data": {"bsonType": ["bool", "null"]},
                                    "has_image_data": {"bsonType": ["bool", "null"]},
                                    "has_critical_history": {"bsonType": ["bool", "null"]}
                                }
                            },
                            "triage": {
                                "bsonType": "object",
                                "properties": {
                                    "score": {"bsonType": "double"},
                                    "priority": {"enum": ["routine", "soon", "urgent", "emergency"]},
                                    "factors": {"bsonType": "array"}
                                }
                            },
                            "privacy": {
                                "bsonType": "object",
                                "properties": {
                                    "pii_detected": {"bsonType": ["bool", "null"]},
                                    "anonymization_required": {"bsonType": ["bool", "null"]},
                                    "compliance_flags": {"bsonType": ["array", "null"]}
                                }
                            },
                            "processing_times": {
                                "bsonType": ["object", "null"],
                                "description": "Processing time for each handler in ms"
                            }
                        }
                    },
                    "created_at": {
                        "bsonType": "date",
                        "description": "Record creation timestamp"
                    }
                }
            }
        },
        "validationLevel": "moderate",
        "validationAction": "warn"
    }
    
    # =================================================================
    # INDEX DEFINITIONS
    # =================================================================
    
    INDEXES = {
        "patients": [
            {"keys": [("patient_id", 1)], "unique": True},
            {"keys": [("codice_fiscale", 1)]},  # Non-unique to allow migration
            {"keys": [("medical_record_number", 1)]},
            {"keys": [("data_nascita", 1)]},
            {"keys": [("created_at", -1)]},
            {"keys": [("allergie", 1)]},
            {"keys": [("malattie_permanenti", 1)]},
        ],
        "patient_records": [
            {"keys": [("encounter_id", 1)], "unique": True},
            {"keys": [("patient_id", 1)]},
            {"keys": [("encounter_timestamp", -1)]},
            {"keys": [("priority", 1)]},
            {"keys": [("patient_id", 1), ("encounter_timestamp", -1)]},  # Compound index
            {"keys": [("processing_context.triage.score", -1)]},
        ]
    }


def get_collection_schemas() -> Dict[str, Any]:
    """
    Get all collection schemas.
    
    Returns:
        Dictionary mapping collection names to their schemas
    """
    return {
        "patients": MongoDBSchemas.PATIENTS_SCHEMA,
        "patient_records": MongoDBSchemas.PATIENT_RECORDS_SCHEMA
    }


def get_indexes() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all index definitions.
    
    Returns:
        Dictionary mapping collection names to their index definitions
    """
    return MongoDBSchemas.INDEXES
