"""Chain of Responsibility pattern implementation for data processing pipeline."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
import time

from ..models.patient import PatientRecord
from ..models.decision import DecisionSupport


class ChainHandler(ABC):
    """Abstract base class for chain handlers."""
    
    def __init__(self):
        self._next_handler: Optional[ChainHandler] = None
        self.handler_name: str = self.__class__.__name__
        self.processing_time_ms: float = 0.0
    
    def set_next(self, handler: 'ChainHandler') -> 'ChainHandler':
        """Set the next handler in the chain."""
        self._next_handler = handler
        return handler
    
    def handle(self, record: PatientRecord, context: dict) -> PatientRecord:
        """Handle the request and pass to next handler."""
        start_time = time.time()
        
        # Process the record
        processed_record = self._process(record, context)
        
        # Track processing time
        self.processing_time_ms = (time.time() - start_time) * 1000
        context.setdefault('processing_times', {})[self.handler_name] = self.processing_time_ms
        
        # Pass to next handler if exists
        if self._next_handler:
            return self._next_handler.handle(processed_record, context)
        
        return processed_record
    
    @abstractmethod
    def _process(self, record: PatientRecord, context: dict) -> PatientRecord:
        """Process the patient record. Must be implemented by subclasses."""
        pass


class ValidationHandler(ChainHandler):
    """Validates clinical data quality and completeness."""
    
    def _process(self, record: PatientRecord, context: dict) -> PatientRecord:
        """Validate all clinical data in the record."""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate patient information
        if not record.patient.patient_id:
            validation_results['errors'].append("Missing patient ID")
            validation_results['is_valid'] = False
        
        # Validate clinical data
        for idx, data in enumerate(record.clinical_data):
            try:
                if not data.validate():
                    validation_results['errors'].append(
                        f"Clinical data {idx} ({data.data_type.value}) failed validation"
                    )
                    validation_results['is_valid'] = False
            except Exception as e:
                validation_results['errors'].append(
                    f"Validation error for data {idx}: {str(e)}"
                )
                validation_results['is_valid'] = False
        
        # Check data completeness
        if len(record.clinical_data) == 0:
            validation_results['warnings'].append("No clinical data provided")
        
        # Add validation results to context
        context['validation'] = validation_results
        
        if not validation_results['is_valid']:
            raise ValueError(f"Validation failed: {', '.join(validation_results['errors'])}")
        
        return record


class EnrichmentHandler(ChainHandler):
    """Enriches clinical data with additional context and metadata."""
    
    def _process(self, record: PatientRecord, context: dict) -> PatientRecord:
        """Enrich the patient record with additional information."""
        enrichment_data = {}
        
        # Calculate patient age if not set
        if record.patient.age is None:
            record.patient.calculate_age()
            enrichment_data['age_calculated'] = True
        
        # Add temporal context
        enrichment_data['processing_timestamp'] = datetime.now().isoformat()
        enrichment_data['data_count'] = len(record.clinical_data)
        
        # Calculate quality scores for clinical data
        quality_scores = []
        for data in record.clinical_data:
            if data.quality_score is None:
                # Simple quality heuristic based on validation
                data.quality_score = 1.0 if data.is_validated else 0.5
            quality_scores.append(data.quality_score)
        
        if quality_scores:
            enrichment_data['average_data_quality'] = sum(quality_scores) / len(quality_scores)
        
        # Add clinical context flags
        enrichment_data['has_text_data'] = any(
            data.data_type.value == 'text' for data in record.clinical_data
        )
        enrichment_data['has_signal_data'] = any(
            data.data_type.value == 'signal' for data in record.clinical_data
        )
        enrichment_data['has_image_data'] = any(
            data.data_type.value == 'image' for data in record.clinical_data
        )
        
        # Check for critical conditions in medical history
        critical_keywords = ['diabetes', 'hypertension', 'cancer', 'cardiac', 'renal']
        enrichment_data['has_critical_history'] = any(
            any(keyword in condition.lower() for keyword in critical_keywords)
            for condition in record.patient.medical_history
        )
        
        context['enrichment'] = enrichment_data
        return record


class TriageHandler(ChainHandler):
    """Performs initial triage to prioritize cases."""
    
    def _process(self, record: PatientRecord, context: dict) -> PatientRecord:
        """Calculate triage score and priority."""
        triage_score = 0.0
        triage_factors = []
        
        # Priority from record
        priority_scores = {
            'emergency': 100,
            'urgent': 75,
            'soon': 50,
            'routine': 25
        }
        base_score = priority_scores.get(record.priority, 25)
        triage_score += base_score
        triage_factors.append(f"Base priority: {record.priority}")
        
        # Age factor (elderly and very young get higher priority)
        if record.patient.age:
            if record.patient.age < 2 or record.patient.age > 75:
                triage_score += 15
                triage_factors.append(f"Age factor: {record.patient.age}")
        
        # Medical history complexity
        if len(record.patient.medical_history) > 3:
            triage_score += 10
            triage_factors.append("Complex medical history")
        
        # Critical history flag from enrichment
        if context.get('enrichment', {}).get('has_critical_history'):
            triage_score += 20
            triage_factors.append("Critical medical history")
        
        # Data quality - lower quality needs more attention
        avg_quality = context.get('enrichment', {}).get('average_data_quality', 1.0)
        if avg_quality < 0.7:
            triage_score += 10
            triage_factors.append("Low data quality")
        
        # Normalize triage score to 0-100
        triage_score = min(triage_score, 100)
        
        # Determine final priority level
        if triage_score >= 90:
            final_priority = 'emergency'
        elif triage_score >= 70:
            final_priority = 'urgent'
        elif triage_score >= 40:
            final_priority = 'soon'
        else:
            final_priority = 'routine'
        
        context['triage'] = {
            'score': triage_score,
            'priority': final_priority,
            'factors': triage_factors
        }
        
        # Update record priority if triage suggests higher priority
        if priority_scores.get(final_priority, 0) > priority_scores.get(record.priority, 0):
            record.priority = final_priority
        
        return record


class DataNormalizationHandler(ChainHandler):
    """Normalizes clinical data to standard formats."""
    
    def _process(self, record: PatientRecord, context: dict) -> PatientRecord:
        """Normalize clinical data formats."""
        normalization_info = {
            'normalized_count': 0,
            'operations': []
        }
        
        # Normalize text data
        for data in record.clinical_data:
            if data.data_type.value == 'text':
                # Basic text normalization
                original_length = len(data.text_content)
                data.text_content = data.text_content.strip()
                if len(data.text_content) != original_length:
                    normalization_info['normalized_count'] += 1
                    normalization_info['operations'].append(f"Trimmed whitespace from text data {data.data_id}")
        
        context['normalization'] = normalization_info
        return record


class PrivacyCheckHandler(ChainHandler):
    """Ensures privacy compliance before processing."""
    
    def _process(self, record: PatientRecord, context: dict) -> PatientRecord:
        """Perform privacy checks."""
        privacy_info = {
            'pii_detected': False,
            'anonymization_required': False,
            'compliance_flags': []
        }
        
        # Check if anonymization is requested
        if context.get('anonymize', False):
            privacy_info['anonymization_required'] = True
            record = record.anonymize()
            privacy_info['compliance_flags'].append("Data anonymized")
        
        # Check for proper consent (placeholder - would check actual consent records)
        if not context.get('consent_verified', True):
            privacy_info['compliance_flags'].append("Consent verification required")
        
        context['privacy'] = privacy_info
        return record
