"""Patient and patient record models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class Gender(Enum):
    """Patient gender."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


@dataclass
class Patient:
    """Patient demographic and clinical information."""
    patient_id: str
    date_of_birth: datetime
    gender: Gender
    medical_record_number: str
    
    # Optional fields
    age: Optional[int] = None
    ethnicity: Optional[str] = None
    primary_language: Optional[str] = "en"
    
    # Clinical context
    chief_complaint: Optional[str] = None
    medical_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    
    def calculate_age(self) -> int:
        """Calculate patient age."""
        today = datetime.now()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        self.age = age
        return age
    
    def anonymize(self) -> 'Patient':
        """Create anonymized patient record."""
        return Patient(
            patient_id="ANONYMIZED",
            date_of_birth=datetime(self.date_of_birth.year, 1, 1),  # Keep year only
            gender=self.gender,
            medical_record_number="ANONYMIZED",
            age=self.age,
            ethnicity=self.ethnicity,
            primary_language=self.primary_language,
            chief_complaint=self.chief_complaint,
            medical_history=self.medical_history.copy(),
            current_medications=self.current_medications.copy(),
            allergies=self.allergies.copy()
        )


@dataclass
class PatientRecord:
    """Complete patient record with clinical data."""
    patient: Patient
    clinical_data: List[Any] = field(default_factory=list)  # List of ClinicalData objects
    encounter_id: Optional[str] = None
    encounter_timestamp: datetime = field(default_factory=datetime.now)
    priority: str = "routine"  # routine, urgent, emergency
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_clinical_data(self, data: Any) -> None:
        """Add clinical data to patient record."""
        self.clinical_data.append(data)
    
    def get_data_by_type(self, data_type: str) -> List[Any]:
        """Retrieve clinical data by type."""
        return [data for data in self.clinical_data if data.data_type.value == data_type]
    
    def anonymize(self) -> 'PatientRecord':
        """Create anonymized patient record."""
        return PatientRecord(
            patient=self.patient.anonymize(),
            clinical_data=[data.anonymize() for data in self.clinical_data],
            encounter_id=self.encounter_id,
            encounter_timestamp=self.encounter_timestamp,
            priority=self.priority,
            metadata=self.metadata.copy()
        )
