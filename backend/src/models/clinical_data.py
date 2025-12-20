"""Clinical data models for text, signals, and images."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class DataType(Enum):
    """Types of clinical data."""
    TEXT = "text"
    SIGNAL = "signal"
    IMAGE = "image"


class DataSource(Enum):
    """Source of clinical data."""
    EHR = "electronic_health_record"
    LAB = "laboratory"
    IMAGING = "imaging"
    WEARABLE = "wearable_device"
    MANUAL = "manual_entry"


@dataclass
class ClinicalData(ABC):
    """Base class for all clinical data."""
    data_id: str
    patient_id: str
    timestamp: datetime
    source: DataSource
    data_type: DataType
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: Optional[float] = None
    is_validated: bool = False
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the clinical data."""
        pass
    
    @abstractmethod
    def anonymize(self) -> 'ClinicalData':
        """Create anonymized version of the data."""
        pass


class TextData(ClinicalData):
    """Clinical text data (notes, reports, transcriptions)."""
    
    def __init__(self, data_id: str, patient_id: str, timestamp: datetime, 
                 source: DataSource, text_content: str, language: str = "en",
                 document_type: Optional[str] = None, metadata: Dict[str, Any] = None,
                 quality_score: Optional[float] = None, is_validated: bool = False):
        self.data_id = data_id
        self.patient_id = patient_id
        self.timestamp = timestamp
        self.source = source
        self.data_type = DataType.TEXT
        self.metadata = metadata or {}
        self.quality_score = quality_score
        self.is_validated = is_validated
        self.text_content = text_content
        self.language = language
        self.document_type = document_type
    
    def validate(self) -> bool:
        """Validate text data."""
        if not self.text_content or len(self.text_content.strip()) == 0:
            return False
        if len(self.text_content) > 1000000:  # Max 1MB text
            return False
        self.is_validated = True
        return True
    
    def anonymize(self) -> 'TextData':
        """Anonymize text data by removing PII."""
        # In production, use NLP-based PII detection
        anonymized_text = self.text_content  # Placeholder
        return TextData(
            data_id=self.data_id,
            patient_id="ANONYMIZED",
            timestamp=self.timestamp,
            source=self.source,
            text_content=anonymized_text,
            language=self.language,
            document_type=self.document_type,
            metadata=self.metadata.copy(),
            quality_score=self.quality_score,
            is_validated=self.is_validated
        )


class SignalData(ClinicalData):
    """Clinical signal data (ECG, EEG, vital signs)."""
    
    def __init__(self, data_id: str, patient_id: str, timestamp: datetime,
                 source: DataSource, signal_values: list, sampling_rate: float,
                 signal_type: str, units: str, duration: float,
                 metadata: Dict[str, Any] = None, quality_score: Optional[float] = None,
                 is_validated: bool = False):
        self.data_id = data_id
        self.patient_id = patient_id
        self.timestamp = timestamp
        self.source = source
        self.data_type = DataType.SIGNAL
        self.metadata = metadata or {}
        self.quality_score = quality_score
        self.is_validated = is_validated
        self.signal_values = signal_values
        self.sampling_rate = sampling_rate
        self.signal_type = signal_type
        self.units = units
        self.duration = duration
    
    def validate(self) -> bool:
        """Validate signal data."""
        if not self.signal_values or len(self.signal_values) == 0:
            return False
        if self.sampling_rate <= 0:
            return False
        # Check for expected duration vs actual samples
        expected_samples = int(self.duration * self.sampling_rate)
        if abs(len(self.signal_values) - expected_samples) > expected_samples * 0.1:
            return False
        self.is_validated = True
        return True
    
    def anonymize(self) -> 'SignalData':
        """Anonymize signal data."""
        return SignalData(
            data_id=self.data_id,
            patient_id="ANONYMIZED",
            timestamp=self.timestamp,
            source=self.source,
            signal_values=self.signal_values.copy() if isinstance(self.signal_values, list) else list(self.signal_values),
            sampling_rate=self.sampling_rate,
            signal_type=self.signal_type,
            units=self.units,
            duration=self.duration,
            metadata=self.metadata.copy(),
            quality_score=self.quality_score,
            is_validated=self.is_validated
        )


class ImageData(ClinicalData):
    """Clinical image data (X-ray, CT, MRI, pathology slides)."""
    
    def __init__(self, data_id: str, patient_id: str, timestamp: datetime,
                 source: DataSource, image_path: str, image_format: str,
                 modality: str, dimensions: tuple, body_part: Optional[str] = None,
                 contrast_used: bool = False, metadata: Dict[str, Any] = None,
                 quality_score: Optional[float] = None, is_validated: bool = False):
        self.data_id = data_id
        self.patient_id = patient_id
        self.timestamp = timestamp
        self.source = source
        self.data_type = DataType.IMAGE
        self.metadata = metadata or {}
        self.quality_score = quality_score
        self.is_validated = is_validated
        self.image_path = image_path
        self.image_format = image_format
        self.modality = modality
        self.dimensions = dimensions
        self.body_part = body_part
        self.contrast_used = contrast_used
    
    def validate(self) -> bool:
        """Validate image data."""
        if not self.image_path:
            return False
        if not all(d > 0 for d in self.dimensions):
            return False
        # In production, verify file exists and is readable
        self.is_validated = True
        return True
    
    def anonymize(self) -> 'ImageData':
        """Anonymize image data by removing DICOM tags."""
        return ImageData(
            data_id=self.data_id,
            patient_id="ANONYMIZED",
            timestamp=self.timestamp,
            source=self.source,
            image_path=self.image_path,
            image_format=self.image_format,
            modality=self.modality,
            dimensions=self.dimensions,
            body_part=self.body_part,
            contrast_used=self.contrast_used,
            metadata={k: v for k, v in self.metadata.items() if k not in ['patient_name', 'patient_dob']},
            quality_score=self.quality_score,
            is_validated=self.is_validated
        )
