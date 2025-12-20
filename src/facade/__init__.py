"""Facade pattern implementation for clinical system integration."""

from .clinical_facade import ClinicalSystemFacade
from .hl7_adapter import HL7Adapter
from .fhir_adapter import FHIRAdapter
from .dicom_adapter import DICOMAdapter

__all__ = [
    'ClinicalSystemFacade',
    'HL7Adapter', 'FHIRAdapter', 'DICOMAdapter'
]
