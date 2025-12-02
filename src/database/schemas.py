"""
MongoDB Schema Definitions for EarlyCare Gateway

This module defines the complete schema structure for storing patient data,
clinical records, and decision support results in MongoDB.

The schemas match the data models and processing pipeline used by the system.
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
                "required": ["patient_id", "date_of_birth", "gender", "medical_record_number"],
                "properties": {
                    "_id": {
                        "bsonType": "objectId",
                        "description": "MongoDB unique identifier"
                    },
                    "patient_id": {
                        "bsonType": "string",
                        "description": "Unique patient identifier (required, indexed)"
                    },
                    "date_of_birth": {
                        "bsonType": "date",
                        "description": "Patient date of birth (required)"
                    },
                    "gender": {
                        "enum": ["male", "female", "other", "unknown"],
                        "description": "Patient gender (required)"
                    },
                    "medical_record_number": {
                        "bsonType": "string",
                        "description": "Medical record number (required, indexed)"
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
                        "description": "Primary language code (default: 'en')"
                    },
                    "medical_history": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        },
                        "description": "List of previous medical conditions"
                    },
                    "allergies_and_diseases": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        },
                        "description": "Allergie e Malattie"
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
    # CLINICAL DATA COLLECTION SCHEMA
    # =================================================================
    
    CLINICAL_DATA_SCHEMA = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["data_id", "patient_id", "timestamp", "source", "data_type"],
                "properties": {
                    "_id": {
                        "bsonType": "objectId"
                    },
                    "data_id": {
                        "bsonType": "string",
                        "description": "Unique data identifier (required, indexed)"
                    },
                    "patient_id": {
                        "bsonType": "string",
                        "description": "Reference to patient (required, indexed)"
                    },
                    "timestamp": {
                        "bsonType": "date",
                        "description": "Data collection timestamp (required, indexed)"
                    },
                    "source": {
                        "enum": ["electronic_health_record", "laboratory", "imaging", 
                                "wearable_device", "manual_entry"],
                        "description": "Data source type (required)"
                    },
                    "data_type": {
                        "enum": ["text", "signal", "image"],
                        "description": "Type of clinical data (required)"
                    },
                    "quality_score": {
                        "bsonType": ["double", "null"],
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Data quality score (0.0-1.0)"
                    },
                    "is_validated": {
                        "bsonType": "bool",
                        "description": "Validation status flag"
                    },
                    "metadata": {
                        "bsonType": "object",
                        "description": "Additional metadata"
                    },
                    # Text data specific fields
                    "text_content": {
                        "bsonType": ["string", "null"],
                        "description": "Text content (for text data type)"
                    },
                    "language": {
                        "bsonType": ["string", "null"],
                        "description": "Language code (for text data)"
                    },
                    "document_type": {
                        "bsonType": ["string", "null"],
                        "description": "Document type (admission note, discharge summary, etc.)"
                    },
                    # Signal data specific fields
                    "signal_values": {
                        "bsonType": ["array", "null"],
                        "description": "Signal data values array (for signal data type)"
                    },
                    "sampling_rate": {
                        "bsonType": ["double", "null"],
                        "description": "Sampling rate in Hz (for signal data)"
                    },
                    "signal_type": {
                        "bsonType": ["string", "null"],
                        "description": "Signal type (ECG, EEG, etc.)"
                    },
                    "units": {
                        "bsonType": ["string", "null"],
                        "description": "Measurement units"
                    },
                    "duration": {
                        "bsonType": ["double", "null"],
                        "description": "Signal duration in seconds"
                    },
                    # Image data specific fields
                    "image_path": {
                        "bsonType": ["string", "null"],
                        "description": "Path to image file (for image data type)"
                    },
                    "image_format": {
                        "bsonType": ["string", "null"],
                        "description": "Image format (DICOM, PNG, JPEG, etc.)"
                    },
                    "modality": {
                        "bsonType": ["string", "null"],
                        "description": "Imaging modality (X-ray, CT, MRI, etc.)"
                    },
                    "dimensions": {
                        "bsonType": ["object", "null"],
                        "description": "Image dimensions (width, height, depth)"
                    },
                    "body_part": {
                        "bsonType": ["string", "null"],
                        "description": "Body part imaged"
                    },
                    "contrast_used": {
                        "bsonType": ["bool", "null"],
                        "description": "Whether contrast was used"
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
                        "description": "Embedded patient information snapshot",
                        "properties": {
                            "patient_id": {"bsonType": "string"},
                            "date_of_birth": {"bsonType": "date"},
                            "gender": {"enum": ["male", "female", "other", "unknown"]},
                            "medical_record_number": {"bsonType": "string"},
                            "age": {"bsonType": ["int", "null"]},
                            "ethnicity": {"bsonType": ["string", "null"]},
                            "primary_language": {"bsonType": "string"},
                            "medical_history": {"bsonType": "array"},
                            "allergies_and_diseases": {"bsonType": "array"}
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
                        "description": "Array of embedded clinical data"
                    },
                    "encounter_timestamp": {
                        "bsonType": "date",
                        "description": "Encounter date/time (required, indexed)"
                    },
                    "priority": {
                        "enum": ["routine", "soon", "urgent", "emergency"],
                        "description": "Clinical priority level (required, indexed)"
                    },
                    "metadata": {
                        "bsonType": "object",
                        "description": "Additional encounter metadata"
                    },
                    # Processing pipeline context
                    "processing_context": {
                        "bsonType": "object",
                        "description": "Context from chain of responsibility processing",
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
    # DECISION SUPPORT COLLECTION SCHEMA
    # =================================================================
    
    DECISION_SUPPORT_SCHEMA = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["request_id", "patient_id", "encounter_id", "timestamp"],
                "properties": {
                    "_id": {
                        "bsonType": "objectId"
                    },
                    "request_id": {
                        "bsonType": "string",
                        "description": "Unique request identifier (required, indexed)"
                    },
                    "patient_id": {
                        "bsonType": "string",
                        "description": "Patient identifier (required, indexed)"
                    },
                    "encounter_id": {
                        "bsonType": "string",
                        "description": "Associated encounter ID (required, indexed)"
                    },
                    "timestamp": {
                        "bsonType": "date",
                        "description": "Decision support generation time (required, indexed)"
                    },
                    # Diagnosis results
                    "diagnoses": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "condition": {"bsonType": "string"},
                                "icd_code": {"bsonType": ["string", "null"]},
                                "confidence_score": {
                                    "bsonType": "double",
                                    "minimum": 0.0,
                                    "maximum": 1.0
                                },
                                "confidence_level": {
                                    "enum": ["very_low", "low", "medium", "high", "very_high"]
                                },
                                "evidence": {"bsonType": "array"},
                                "risk_factors": {"bsonType": "array"},
                                "differential_diagnoses": {"bsonType": "array"},
                                "recommended_tests": {"bsonType": "array"},
                                "recommended_specialists": {"bsonType": "array"}
                            }
                        },
                        "description": "List of diagnosis results"
                    },
                    # Triage information
                    "urgency_level": {
                        "enum": ["routine", "soon", "urgent", "emergency"],
                        "description": "Clinical urgency level (indexed)"
                    },
                    "triage_score": {
                        "bsonType": "double",
                        "minimum": 0.0,
                        "maximum": 100.0,
                        "description": "Computed triage score (0-100)"
                    },
                    # Clinical decision support
                    "alerts": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "Critical alerts requiring immediate attention"
                    },
                    "warnings": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "Warning messages"
                    },
                    "clinical_notes": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "Additional clinical notes"
                    },
                    # Model traceability
                    "models_used": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"},
                        "description": "List of AI models used in analysis"
                    },
                    "processing_time_ms": {
                        "bsonType": "double",
                        "description": "Total processing time in milliseconds"
                    },
                    # Explainability
                    "explanation": {
                        "bsonType": ["string", "null"],
                        "description": "Human-readable explanation of decision"
                    },
                    "feature_importance": {
                        "bsonType": ["object", "null"],
                        "description": "Feature importance scores for explainability"
                    },
                    # Metadata
                    "metadata": {
                        "bsonType": "object",
                        "description": "Additional metadata"
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
    # AUDIT LOG COLLECTION SCHEMA
    # =================================================================
    
    AUDIT_LOG_SCHEMA = {
        "validator": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["event_id", "timestamp", "event_type", "user_id"],
                "properties": {
                    "_id": {
                        "bsonType": "objectId"
                    },
                    "event_id": {
                        "bsonType": "string",
                        "description": "Unique event identifier (required, indexed)"
                    },
                    "timestamp": {
                        "bsonType": "date",
                        "description": "Event timestamp (required, indexed)"
                    },
                    "event_type": {
                        "enum": ["access", "create", "update", "delete", "export", 
                                "anonymize", "process", "error"],
                        "description": "Type of audit event (required, indexed)"
                    },
                    "user_id": {
                        "bsonType": "string",
                        "description": "User who performed the action (required, indexed)"
                    },
                    "patient_id": {
                        "bsonType": ["string", "null"],
                        "description": "Affected patient ID (indexed)"
                    },
                    "resource_type": {
                        "bsonType": ["string", "null"],
                        "description": "Type of resource affected"
                    },
                    "resource_id": {
                        "bsonType": ["string", "null"],
                        "description": "ID of affected resource"
                    },
                    "action": {
                        "bsonType": "string",
                        "description": "Detailed action description"
                    },
                    "ip_address": {
                        "bsonType": ["string", "null"],
                        "description": "IP address of the user"
                    },
                    "success": {
                        "bsonType": "bool",
                        "description": "Whether the action succeeded"
                    },
                    "error_message": {
                        "bsonType": ["string", "null"],
                        "description": "Error message if action failed"
                    },
                    "metadata": {
                        "bsonType": "object",
                        "description": "Additional audit metadata"
                    }
                }
            }
        },
        "validationLevel": "strict",
        "validationAction": "error"
    }
    
    # =================================================================
    # INDEX DEFINITIONS
    # =================================================================
    
    INDEXES = {
        "patients": [
            {"keys": [("patient_id", 1)], "unique": True},
            {"keys": [("medical_record_number", 1)]},
            {"keys": [("date_of_birth", 1)]},
            {"keys": [("created_at", -1)]},
            {"keys": [("allergies_and_diseases", 1)]},  # For allergy/disease queries
        ],
        "patient_records": [
            {"keys": [("encounter_id", 1)], "unique": True},
            {"keys": [("patient_id", 1)]},
            {"keys": [("encounter_timestamp", -1)]},
            {"keys": [("priority", 1)]},
            {"keys": [("patient_id", 1), ("encounter_timestamp", -1)]},  # Compound
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
