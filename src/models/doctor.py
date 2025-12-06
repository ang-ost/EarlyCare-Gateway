"""
Doctor/Physician model for authentication and management
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import hashlib
import secrets


@dataclass
class Doctor:
    """
    Represents a doctor/physician user
    """
    doctor_id: str  # Unique ID (auto-generated)
    nome: str
    cognome: str
    specializzazione: str
    ospedale_affiliato: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return Doctor.hash_password(password) == password_hash

    @staticmethod
    def generate_doctor_id(nome: str, cognome: str) -> str:
        """
        Generate unique doctor ID based on name and random component.
        Format: FirstLetter_LastName_RandomString
        Example: M_Rossi_abc123xyz
        """
        first_letter = nome[0].upper() if nome else 'X'
        last_name = cognome.upper()[:6] if cognome else 'XXXX'
        # Generate random suffix (6 alphanumeric characters)
        random_suffix = secrets.token_hex(3).upper()  # 6 hex chars
        
        doctor_id = f"{first_letter}_{last_name}_{random_suffix}"
        return doctor_id

    def to_dict(self) -> dict:
        """Convert to dictionary for storage/serialization"""
        return {
            'doctor_id': self.doctor_id,
            'nome': self.nome,
            'cognome': self.cognome,
            'specializzazione': self.specializzazione,
            'ospedale_affiliato': self.ospedale_affiliato,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Doctor':
        """Create instance from dictionary"""
        return cls(
            doctor_id=data['doctor_id'],
            nome=data['nome'],
            cognome=data['cognome'],
            specializzazione=data['specializzazione'],
            ospedale_affiliato=data['ospedale_affiliato'],
            password_hash=data['password_hash'],
            created_at=data.get('created_at', datetime.now()),
            last_login=data.get('last_login'),
            is_active=data.get('is_active', True)
        )
