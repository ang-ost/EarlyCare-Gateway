"""Decision support and diagnosis result models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence level for diagnosis."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class UrgencyLevel(Enum):
    """Urgency level for medical attention."""
    ROUTINE = "routine"
    SOON = "soon"
    URGENT = "urgent"
    EMERGENCY = "emergency"


@dataclass
class DiagnosisResult:
    """Single diagnosis result with confidence and supporting evidence."""
    condition: str
    icd_code: Optional[str] = None
    confidence_score: float = 0.0  # 0.0 to 1.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    # Supporting information
    evidence: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    differential_diagnoses: List[str] = field(default_factory=list)
    
    # Recommendations
    recommended_tests: List[str] = field(default_factory=list)
    recommended_specialists: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Set confidence level based on score."""
        if self.confidence_score >= 0.9:
            self.confidence_level = ConfidenceLevel.VERY_HIGH
        elif self.confidence_score >= 0.7:
            self.confidence_level = ConfidenceLevel.HIGH
        elif self.confidence_score >= 0.5:
            self.confidence_level = ConfidenceLevel.MEDIUM
        elif self.confidence_score >= 0.3:
            self.confidence_level = ConfidenceLevel.LOW
        else:
            self.confidence_level = ConfidenceLevel.VERY_LOW


@dataclass
class DecisionSupport:
    """Decision support output from the gateway."""
    request_id: str
    patient_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Primary diagnosis results
    diagnoses: List[DiagnosisResult] = field(default_factory=list)
    
    # Triage information
    urgency_level: UrgencyLevel = UrgencyLevel.ROUTINE
    triage_score: float = 0.0
    
    # Clinical decision support
    alerts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    clinical_notes: List[str] = field(default_factory=list)
    
    # Model information for traceability
    models_used: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    
    # Explainability
    explanation: Optional[str] = None
    feature_importance: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_diagnosis(self, diagnosis: DiagnosisResult) -> None:
        """Add a diagnosis result."""
        self.diagnoses.append(diagnosis)
        # Update urgency based on highest confidence diagnosis
        if diagnosis.confidence_score > 0.8:
            self._update_urgency(diagnosis)
    
    def _update_urgency(self, diagnosis: DiagnosisResult) -> None:
        """Update urgency level based on diagnosis."""
        # Simple heuristic - in production, use clinical decision rules
        if any(term in diagnosis.condition.lower() for term in ['sepsis', 'stroke', 'infarction']):
            self.urgency_level = UrgencyLevel.EMERGENCY
        elif any(term in diagnosis.condition.lower() for term in ['pneumonia', 'fracture']):
            self.urgency_level = UrgencyLevel.URGENT
    
    def get_top_diagnosis(self) -> Optional[DiagnosisResult]:
        """Get the diagnosis with highest confidence."""
        if not self.diagnoses:
            return None
        return max(self.diagnoses, key=lambda d: d.confidence_score)
    
    def add_alert(self, alert: str) -> None:
        """Add a clinical alert."""
        self.alerts.append(alert)
    
    def add_warning(self, warning: str) -> None:
        """Add a clinical warning."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'request_id': self.request_id,
            'patient_id': self.patient_id,
            'timestamp': self.timestamp.isoformat(),
            'diagnoses': [
                {
                    'condition': d.condition,
                    'icd_code': d.icd_code,
                    'confidence_score': d.confidence_score,
                    'confidence_level': d.confidence_level.value,
                    'evidence': d.evidence,
                    'recommended_tests': d.recommended_tests
                }
                for d in self.diagnoses
            ],
            'urgency_level': self.urgency_level.value,
            'triage_score': self.triage_score,
            'alerts': self.alerts,
            'warnings': self.warnings,
            'models_used': self.models_used,
            'processing_time_ms': self.processing_time_ms,
            'explanation': self.explanation,
            'metadata': self.metadata
        }
