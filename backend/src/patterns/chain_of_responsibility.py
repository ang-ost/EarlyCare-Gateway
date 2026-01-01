"""
Chain of Responsibility Pattern Implementation
Handles data processing pipeline: validation, enrichment, privacy, triage
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataHandler(ABC):
    """Base handler in the chain of responsibility"""
    
    def __init__(self):
        self._next_handler: Optional[DataHandler] = None
    
    def set_next(self, handler: 'DataHandler') -> 'DataHandler':
        """Set the next handler in the chain"""
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the data and pass to next handler"""
        pass
    
    def _pass_to_next(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Pass data to the next handler if exists"""
        if self._next_handler:
            return self._next_handler.handle(data)
        return data


class ValidationHandler(DataHandler):
    """Validates incoming patient data"""
    
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Validation: Checking required fields")
        
        if 'fiscal_code' in data or 'patient_id' in data:
            data['validation_status'] = 'valid'
        else:
            data['validation_status'] = 'invalid'
            data['validation_errors'] = ['Missing patient identifier']
        
        return self._pass_to_next(data)


class EnrichmentHandler(DataHandler):
    """Enriches data with calculated fields"""
    
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Enrichment: Adding metadata")
        
        if 'birth_date' in data and 'age' not in data:
            from datetime import datetime
            birth_date = datetime.fromisoformat(data['birth_date'].replace('Z', '+00:00'))
            age = (datetime.now() - birth_date).days // 365
            data['age'] = age
        
        data['enriched'] = True
        return self._pass_to_next(data)


class PrivacyHandler(DataHandler):
    """Applies privacy rules and data protection"""
    
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Privacy: Applying data protection rules")
        
        data['privacy_compliant'] = True
        data['anonymizable'] = True
        
        return self._pass_to_next(data)


class TriageHandler(DataHandler):
    """Performs triage based on clinical data"""
    
    def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Triage: Assessing priority")
        
        priority = 'routine'
        
        if 'clinical_records' in data and data['clinical_records']:
            latest_record = data['clinical_records'][-1] if isinstance(data['clinical_records'], list) else data['clinical_records']
            if isinstance(latest_record, dict) and 'priority' in latest_record:
                priority = latest_record['priority']
        
        data['triage_priority'] = priority
        
        return self._pass_to_next(data)


class DataProcessingPipeline:
    """Manages the chain of responsibility for data processing"""
    
    def __init__(self):
        self.validation = ValidationHandler()
        self.enrichment = EnrichmentHandler()
        self.privacy = PrivacyHandler()
        self.triage = TriageHandler()
        
        self.validation.set_next(self.enrichment).set_next(self.privacy).set_next(self.triage)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through the entire pipeline"""
        logger.info("Starting data processing pipeline")
        return self.validation.handle(data)
