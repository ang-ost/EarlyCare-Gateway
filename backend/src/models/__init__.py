"""Domain models for clinical data and patient records."""

from .patient import Patient, PatientRecord
from .doctor import Doctor

__all__ = [
    'Patient', 'PatientRecord',
    'Doctor'
]

