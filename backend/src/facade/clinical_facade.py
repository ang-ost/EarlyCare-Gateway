"""Facade pattern for clinical system integration."""

from typing import Dict, Any, Optional
from datetime import datetime

from ..models.patient import PatientRecord
from ..models.decision import DecisionSupport
from .hl7_adapter import HL7Adapter
from .fhir_adapter import FHIRAdapter
from .dicom_adapter import DICOMAdapter


class ClinicalSystemFacade:
    """
    Facade for integrating with various clinical systems.
    Provides a unified interface for HL7, FHIR, DICOM, and other protocols.
    """
    
    def __init__(self):
        self.hl7_adapter = HL7Adapter()
        self.fhir_adapter = FHIRAdapter()
        self.dicom_adapter = DICOMAdapter()
        self.connected_systems: Dict[str, bool] = {}
    
    def connect_to_system(self, system_type: str, config: Dict[str, Any]) -> bool:
        """
        Connect to a clinical system.
        
        Args:
            system_type: Type of system (hl7, fhir, dicom)
            config: Connection configuration
            
        Returns:
            True if connection successful
        """
        try:
            if system_type.lower() == 'hl7':
                success = self.hl7_adapter.connect(config)
            elif system_type.lower() == 'fhir':
                success = self.fhir_adapter.connect(config)
            elif system_type.lower() == 'dicom':
                success = self.dicom_adapter.connect(config)
            else:
                raise ValueError(f"Unsupported system type: {system_type}")
            
            self.connected_systems[system_type] = success
            return success
        except Exception as e:
            print(f"Error connecting to {system_type}: {e}")
            return False
    
    def import_patient_data(
        self,
        system_type: str,
        patient_id: str,
        data_types: Optional[list] = None
    ) -> PatientRecord:
        """
        Import patient data from clinical system.
        
        Args:
            system_type: Type of system to import from
            patient_id: Patient identifier
            data_types: Optional list of specific data types to import
            
        Returns:
            PatientRecord with imported data
        """
        if system_type.lower() == 'hl7':
            return self.hl7_adapter.import_patient_data(patient_id, data_types)
        elif system_type.lower() == 'fhir':
            return self.fhir_adapter.import_patient_data(patient_id, data_types)
        elif system_type.lower() == 'dicom':
            return self.dicom_adapter.import_patient_data(patient_id, data_types)
        else:
            raise ValueError(f"Unsupported system type: {system_type}")
    
    def export_decision_support(
        self,
        system_type: str,
        decision_support: DecisionSupport,
        destination: str
    ) -> bool:
        """
        Export decision support results to clinical system.
        
        Args:
            system_type: Type of system to export to
            decision_support: Decision support results
            destination: Destination identifier (patient chart, order system, etc.)
            
        Returns:
            True if export successful
        """
        try:
            if system_type.lower() == 'hl7':
                return self.hl7_adapter.export_results(decision_support, destination)
            elif system_type.lower() == 'fhir':
                return self.fhir_adapter.export_results(decision_support, destination)
            else:
                raise ValueError(f"Export not supported for system type: {system_type}")
        except Exception as e:
            print(f"Error exporting to {system_type}: {e}")
            return False
    
    def query_clinical_data(
        self,
        system_type: str,
        query_params: Dict[str, Any]
    ) -> list:
        """
        Query clinical data from system.
        
        Args:
            system_type: Type of system to query
            query_params: Query parameters
            
        Returns:
            List of matching records
        """
        if system_type.lower() == 'hl7':
            return self.hl7_adapter.query(query_params)
        elif system_type.lower() == 'fhir':
            return self.fhir_adapter.query(query_params)
        elif system_type.lower() == 'dicom':
            return self.dicom_adapter.query(query_params)
        else:
            raise ValueError(f"Unsupported system type: {system_type}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all connected systems."""
        return {
            'connected_systems': self.connected_systems,
            'hl7_status': self.hl7_adapter.get_status(),
            'fhir_status': self.fhir_adapter.get_status(),
            'dicom_status': self.dicom_adapter.get_status(),
            'timestamp': datetime.now().isoformat()
        }
    
    def disconnect_all(self):
        """Disconnect from all systems."""
        self.hl7_adapter.disconnect()
        self.fhir_adapter.disconnect()
        self.dicom_adapter.disconnect()
        self.connected_systems.clear()
