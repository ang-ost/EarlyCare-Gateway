"""Strategy pattern for swappable AI model selection."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from ..models.patient import PatientRecord
from ..models.decision import DecisionSupport, DiagnosisResult


class ModelStrategy(ABC):
    """Abstract base class for model strategies."""
    
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.model_version: str = "1.0.0"
        self.confidence_threshold: float = 0.5
    
    @abstractmethod
    def execute(
        self,
        record: PatientRecord,
        decision_support: DecisionSupport,
        context: Dict[str, Any]
    ) -> DecisionSupport:
        """
        Execute the model strategy on patient record.
        
        Args:
            record: Patient record to analyze
            decision_support: Decision support object to populate
            context: Processing context
            
        Returns:
            Updated DecisionSupport object
        """
        pass
    
    @abstractmethod
    def can_handle(self, record: PatientRecord, context: Dict[str, Any]) -> bool:
        """
        Determine if this strategy can handle the given record.
        
        Args:
            record: Patient record
            context: Processing context
            
        Returns:
            True if strategy can handle this record
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        return {
            'strategy_name': self.strategy_name,
            'model_version': self.model_version,
            'confidence_threshold': self.confidence_threshold
        }


class PathologyStrategy(ModelStrategy):
    """Strategy for pathology-specific models (cancer, tissue analysis)."""
    
    def __init__(self, pathology_type: str):
        super().__init__(f"pathology_{pathology_type}")
        self.pathology_type = pathology_type
        self.supported_modalities = ['PATHOLOGY', 'MRI', 'CT']
    
    def can_handle(self, record: PatientRecord, context: Dict[str, Any]) -> bool:
        """Check if record contains pathology-relevant data."""
        # Check for image data with pathology modality
        for data in record.clinical_data:
            if hasattr(data, 'modality') and data.modality in self.supported_modalities:
                return True
        
        # Check for relevant keywords in text data
        keywords = ['biopsy', 'tumor', 'lesion', 'pathology', self.pathology_type]
        for data in record.clinical_data:
            if hasattr(data, 'text_content'):
                text_lower = data.text_content.lower()
                if any(keyword in text_lower for keyword in keywords):
                    return True
        
        return False
    
    def execute(
        self,
        record: PatientRecord,
        decision_support: DecisionSupport,
        context: Dict[str, Any]
    ) -> DecisionSupport:
        """Execute pathology analysis."""
        # Placeholder for actual ML model execution
        # In production, this would call a trained model
        
        diagnosis = DiagnosisResult(
            condition=f"{self.pathology_type.capitalize()} Analysis Required",
            confidence_score=0.75,
            evidence=["Pathology imaging detected", "Clinical indicators present"],
            recommended_tests=["Detailed pathology review", "Molecular testing"],
            recommended_specialists=["Pathologist", "Oncologist"]
        )
        
        decision_support.add_diagnosis(diagnosis)
        decision_support.explanation = f"Pathology analysis for {self.pathology_type} completed"
        
        return decision_support


class DeviceStrategy(ModelStrategy):
    """Strategy for device-specific models (wearables, monitoring equipment)."""
    
    def __init__(self, device_type: str):
        super().__init__(f"device_{device_type}")
        self.device_type = device_type
        self.signal_types = []
        
        # Map device types to signal types
        if device_type == "cardiac":
            self.signal_types = ["ECG", "EKG"]
        elif device_type == "neurological":
            self.signal_types = ["EEG"]
        elif device_type == "respiratory":
            self.signal_types = ["SpO2", "Respiration"]
    
    def can_handle(self, record: PatientRecord, context: Dict[str, Any]) -> bool:
        """Check if record contains device-specific signal data."""
        for data in record.clinical_data:
            if hasattr(data, 'signal_type') and data.signal_type in self.signal_types:
                return True
        return False
    
    def execute(
        self,
        record: PatientRecord,
        decision_support: DecisionSupport,
        context: Dict[str, Any]
    ) -> DecisionSupport:
        """Execute device-specific signal analysis."""
        # Placeholder for signal processing
        
        # Analyze signals
        for data in record.clinical_data:
            if hasattr(data, 'signal_type') and data.signal_type in self.signal_types:
                # Mock analysis
                diagnosis = DiagnosisResult(
                    condition=f"Abnormal {data.signal_type} Pattern",
                    confidence_score=0.68,
                    evidence=[f"{data.signal_type} signal analysis", "Pattern recognition"],
                    recommended_tests=[f"Extended {data.signal_type} monitoring"],
                    recommended_specialists=["Cardiologist" if self.device_type == "cardiac" else "Specialist"]
                )
                decision_support.add_diagnosis(diagnosis)
        
        decision_support.explanation = f"Device analysis for {self.device_type} signals completed"
        return decision_support


class DomainStrategy(ModelStrategy):
    """Strategy for domain-specific models (radiology, cardiology, etc.)."""
    
    def __init__(self, domain: str):
        super().__init__(f"domain_{domain}")
        self.domain = domain
        self.keywords = self._get_domain_keywords()
    
    def _get_domain_keywords(self) -> List[str]:
        """Get keywords for this domain."""
        keyword_map = {
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'chest pain', 'ecg'],
            'neurology': ['brain', 'neurological', 'seizure', 'stroke', 'headache'],
            'pulmonology': ['lung', 'respiratory', 'breathing', 'pneumonia', 'copd'],
            'oncology': ['cancer', 'tumor', 'malignancy', 'chemotherapy', 'radiation'],
            'radiology': ['x-ray', 'ct', 'mri', 'imaging', 'scan'],
            'general': []  # Empty keywords means it matches everything
        }
        return keyword_map.get(self.domain, [])
    
    def can_handle(self, record: PatientRecord, context: Dict[str, Any]) -> bool:
        """Check if record is relevant to this domain."""
        # General domain accepts everything
        if self.domain == 'general':
            return True
        
        # If no keywords, accept everything
        if not self.keywords:
            return True
            
        # Check chief complaint
        if record.chief_complaint:
            complaint_lower = record.chief_complaint.lower()
            if any(keyword in complaint_lower for keyword in self.keywords):
                return True
        
        # Check text data
        for data in record.clinical_data:
            if hasattr(data, 'text_content'):
                text_lower = data.text_content.lower()
                if any(keyword in text_lower for keyword in self.keywords):
                    return True
        
        # Check medical history (malattie_permanenti)
        for condition in record.patient.malattie_permanenti:
            condition_lower = condition.lower()
            if any(keyword in condition_lower for keyword in self.keywords):
                return True
        
        return False
    
    def execute(
        self,
        record: PatientRecord,
        decision_support: DecisionSupport,
        context: Dict[str, Any]
    ) -> DecisionSupport:
        """Execute domain-specific analysis."""
        # Placeholder for domain model execution
        
        diagnosis = DiagnosisResult(
            condition=f"{self.domain.capitalize()} Condition Detected",
            confidence_score=0.72,
            evidence=[f"{self.domain.capitalize()} indicators found", "Clinical correlation"],
            recommended_tests=[f"{self.domain.capitalize()} specialist consultation"],
            recommended_specialists=[f"{self.domain.capitalize()} specialist"]
        )
        
        decision_support.add_diagnosis(diagnosis)
        decision_support.explanation = f"Domain analysis for {self.domain} completed"
        decision_support.feature_importance = {
            'chief_complaint': 0.3,
            'medical_history': 0.2,
            'clinical_data': 0.5
        }
        
        return decision_support


class EnsembleStrategy(ModelStrategy):
    """Strategy that combines multiple models."""
    
    def __init__(self, strategies: List[ModelStrategy]):
        super().__init__("ensemble")
        self.strategies = strategies
    
    def can_handle(self, record: PatientRecord, context: Dict[str, Any]) -> bool:
        """Ensemble can handle if any sub-strategy can handle."""
        return any(strategy.can_handle(record, context) for strategy in self.strategies)
    
    def execute(
        self,
        record: PatientRecord,
        decision_support: DecisionSupport,
        context: Dict[str, Any]
    ) -> DecisionSupport:
        """Execute all applicable strategies and combine results."""
        applicable_strategies = [
            s for s in self.strategies if s.can_handle(record, context)
        ]
        
        for strategy in applicable_strategies:
            decision_support = strategy.execute(record, decision_support, context)
            decision_support.models_used.append(strategy.strategy_name)
        
        decision_support.explanation = f"Ensemble of {len(applicable_strategies)} models"
        return decision_support
