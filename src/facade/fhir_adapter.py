"""FHIR adapter for modern healthcare interoperability."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from ..models.patient import Patient, PatientRecord, Gender
from ..models.clinical_data import TextData, DataSource


class FHIRAdapter:
    """Adapter for FHIR (Fast Healthcare Interoperability Resources) R4."""
    
    def __init__(self):
        self.connected = False
        self.base_url: str = ""
        self.api_key: Optional[str] = None
        self.requests_made = 0
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        Connect to FHIR server.
        
        Args:
            config: Configuration with base_url, api_key, etc.
            
        Returns:
            True if successful
        """
        # In production, use fhir.resources library
        self.base_url = config.get('base_url', '')
        self.api_key = config.get('api_key')
        
        # Test connection with capability statement
        # Would do: GET {base_url}/metadata
        
        self.connected = True
        return True
    
    def disconnect(self):
        """Disconnect from FHIR server."""
        self.connected = False
    
    def import_patient_data(
        self,
        patient_id: str,
        data_types: Optional[List[str]] = None
    ) -> PatientRecord:
        """
        Import patient data from FHIR server.
        
        Args:
            patient_id: FHIR Patient resource ID
            data_types: Resource types to import (Observation, DiagnosticReport, etc.)
            
        Returns:
            PatientRecord with imported data
        """
        if not self.connected:
            raise ConnectionError("Not connected to FHIR server")
        
        # Placeholder for FHIR API calls
        # Would do: GET {base_url}/Patient/{patient_id}
        patient_resource = self._get_patient_resource(patient_id)
        
        # Convert FHIR resource to our model
        patient = self._fhir_to_patient(patient_resource)
        record = PatientRecord(patient=patient)
        
        # Import additional resources
        if not data_types:
            data_types = ['Observation', 'DiagnosticReport', 'DocumentReference']
        
        for resource_type in data_types:
            resources = self._search_resources(resource_type, patient_id)
            for resource in resources:
                clinical_data = self._fhir_to_clinical_data(resource)
                if clinical_data:
                    record.add_clinical_data(clinical_data)
        
        return record
    
    def _get_patient_resource(self, patient_id: str) -> Dict[str, Any]:
        """Get FHIR Patient resource."""
        # Placeholder - would make actual HTTP request
        return {
            'resourceType': 'Patient',
            'id': patient_id,
            'name': [{'family': 'Doe', 'given': ['John']}],
            'gender': 'male',
            'birthDate': '1980-01-01'
        }
    
    def _search_resources(
        self,
        resource_type: str,
        patient_id: str
    ) -> List[Dict[str, Any]]:
        """Search for FHIR resources."""
        # Placeholder - would make actual HTTP request
        # GET {base_url}/{resource_type}?patient={patient_id}
        self.requests_made += 1
        return []
    
    def _fhir_to_patient(self, fhir_resource: Dict[str, Any]) -> Patient:
        """Convert FHIR Patient resource to our Patient model."""
        gender_map = {
            'male': Gender.MALE,
            'female': Gender.FEMALE,
            'other': Gender.OTHER,
            'unknown': Gender.UNKNOWN
        }
        
        birth_date_str = fhir_resource.get('birthDate', '2000-01-01')
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        
        return Patient(
            patient_id=fhir_resource['id'],
            date_of_birth=birth_date,
            gender=gender_map.get(fhir_resource.get('gender', 'unknown'), Gender.UNKNOWN),
            medical_record_number=fhir_resource['id']
        )
    
    def _fhir_to_clinical_data(self, fhir_resource: Dict[str, Any]) -> Optional[Any]:
        """Convert FHIR resource to clinical data."""
        resource_type = fhir_resource.get('resourceType')
        
        if resource_type == 'DocumentReference':
            # Convert to TextData
            return TextData(
                data_id=fhir_resource['id'],
                patient_id=fhir_resource.get('subject', {}).get('reference', '').split('/')[-1],
                timestamp=datetime.now(),
                source=DataSource.EHR,
                text_content="Document content from FHIR",
                document_type=fhir_resource.get('type', {}).get('text', 'unknown')
            )
        
        # Add handlers for other resource types
        return None
    
    def export_results(
        self,
        decision_support: Any,
        destination: str
    ) -> bool:
        """
        Export decision support as FHIR resources.
        
        Args:
            decision_support: DecisionSupport object
            destination: Patient resource ID
            
        Returns:
            True if successful
        """
        if not self.connected:
            raise ConnectionError("Not connected to FHIR server")
        
        # Create FHIR DiagnosticReport or ClinicalImpression
        fhir_resources = self._create_fhir_diagnostic_report(decision_support, destination)
        
        # Would POST to FHIR server
        # POST {base_url}/DiagnosticReport
        
        self.requests_made += 1
        return True
    
    def _create_fhir_diagnostic_report(
        self,
        decision_support: Any,
        patient_id: str
    ) -> Dict[str, Any]:
        """Create FHIR DiagnosticReport from decision support."""
        return {
            'resourceType': 'DiagnosticReport',
            'id': decision_support.request_id,
            'status': 'final',
            'code': {
                'coding': [{
                    'system': 'http://loinc.org',
                    'code': 'LP29708-2',
                    'display': 'Cardiology'
                }]
            },
            'subject': {'reference': f'Patient/{patient_id}'},
            'effectiveDateTime': decision_support.timestamp.isoformat(),
            'issued': datetime.now().isoformat(),
            'conclusion': decision_support.explanation or 'AI-assisted diagnosis',
            'conclusionCode': [
                {
                    'coding': [{
                        'display': d.condition,
                        'code': d.icd_code or 'unknown'
                    }]
                }
                for d in decision_support.diagnoses
            ]
        }
    
    def query(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query FHIR server.
        
        Args:
            query_params: FHIR search parameters
            
        Returns:
            List of FHIR resources
        """
        if not self.connected:
            raise ConnectionError("Not connected to FHIR server")
        
        # Placeholder for FHIR search
        self.requests_made += 1
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get FHIR adapter status."""
        return {
            'connected': self.connected,
            'protocol': 'FHIR R4',
            'base_url': self.base_url,
            'requests_made': self.requests_made,
            'authenticated': self.api_key is not None
        }
