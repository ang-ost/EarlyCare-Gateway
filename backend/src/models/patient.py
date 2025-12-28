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
    # Campi obbligatori
    patient_id: str
    nome: str
    cognome: str
    data_nascita: datetime
    comune_nascita: str
    codice_fiscale: str
    
    # Campi opzionali
    data_decesso: Optional[datetime] = None
    allergie: List[str] = field(default_factory=list)
    malattie_permanenti: List[str] = field(default_factory=list)
    
    # Altri campi opzionali
    gender: Optional[Gender] = None
    medical_record_number: Optional[str] = None
    age: Optional[int] = None
    ethnicity: Optional[str] = None
    primary_language: Optional[str] = "it"
    is_foreign: bool = False
    
    def calculate_age(self) -> int:
        """Calculate patient age."""
        today = datetime.now()
        age = today.year - self.data_nascita.year
        if (today.month, today.day) < (self.data_nascita.month, self.data_nascita.day):
            age -= 1
        self.age = age
        return age

    @staticmethod
    def generate_foreign_id(nome: str, cognome: str) -> str:
        """
        Generate unique foreign patient ID.
        Format: FirstLetterLastLetterRandomChars (6 chars total)
        """
        import string
        import secrets
        first_letter_nome = nome[0].upper() if nome else 'X'
        first_letter_cognome = cognome[0].upper() if cognome else 'X'
        
        # Generate 4 random alphanumeric characters
        chars = string.ascii_uppercase + string.digits
        random_suffix = ''.join(secrets.choice(chars) for _ in range(4))
        
        return f"{first_letter_nome}{first_letter_cognome}{random_suffix}"
    
    def anonymize(self) -> 'Patient':
        """Create anonymized patient record."""
        return Patient(
            patient_id="ANONYMIZED",
            nome="ANONYMIZED",
            cognome="ANONYMIZED",
            data_nascita=datetime(self.data_nascita.year, 1, 1),  # Keep year only
            comune_nascita="ANONYMIZED",
            codice_fiscale="ANONYMIZED",
            data_decesso=self.data_decesso,
            allergie=self.allergie.copy(),
            malattie_permanenti=self.malattie_permanenti.copy(),
            gender=self.gender,
            medical_record_number="ANONYMIZED" if self.medical_record_number else None,
            age=self.age,
            ethnicity=self.ethnicity,
            primary_language=self.primary_language,
            is_foreign=self.is_foreign
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
    
    # Encounter-specific fields (moved from Patient)
    chief_complaint: Optional[str] = None
    current_medications: List[str] = field(default_factory=list)
    
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
