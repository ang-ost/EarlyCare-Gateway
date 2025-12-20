"""Data anonymization utilities for HIPAA compliance."""

import re
import hashlib
from typing import Dict, Any, List, Set
from datetime import datetime


class DataAnonymizer:
    """
    Handles anonymization of patient data for privacy compliance.
    Removes or transforms PII while maintaining clinical utility.
    """
    
    def __init__(self):
        self.pii_patterns = self._initialize_pii_patterns()
        self.anonymization_map: Dict[str, str] = {}
        self.hash_salt = "earlycare_gateway_salt"  # In production, use secure random salt
    
    def _initialize_pii_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for common PII."""
        return {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'mrn': r'\b[A-Z]{2,3}\d{6,10}\b',
            'date': r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            'zip_code': r'\b\d{5}(-\d{4})?\b'
        }
    
    def anonymize_text(self, text: str, preserve_dates: bool = False) -> str:
        """
        Anonymize PII in text while preserving clinical information.
        
        Args:
            text: Input text with potential PII
            preserve_dates: Whether to preserve date information
            
        Returns:
            Anonymized text
        """
        anonymized = text
        
        # Replace SSN
        anonymized = re.sub(self.pii_patterns['ssn'], '[SSN-REDACTED]', anonymized)
        
        # Replace phone numbers
        anonymized = re.sub(self.pii_patterns['phone'], '[PHONE-REDACTED]', anonymized)
        
        # Replace email addresses
        anonymized = re.sub(self.pii_patterns['email'], '[EMAIL-REDACTED]', anonymized)
        
        # Replace MRN
        anonymized = re.sub(self.pii_patterns['mrn'], '[MRN-REDACTED]', anonymized)
        
        # Replace dates if not preserving
        if not preserve_dates:
            anonymized = re.sub(self.pii_patterns['date'], '[DATE-REDACTED]', anonymized)
        
        # Replace names (simple approach - in production use NER)
        anonymized = self._replace_common_names(anonymized)
        
        return anonymized
    
    def _replace_common_names(self, text: str) -> str:
        """Replace common first names with placeholder."""
        # Simple implementation - in production, use NLP/NER
        common_names = ['John', 'Jane', 'Mary', 'Michael', 'David', 'Sarah']
        for name in common_names:
            text = re.sub(r'\b' + name + r'\b', '[NAME]', text, flags=re.IGNORECASE)
        return text
    
    def generate_pseudonym(self, identifier: str, id_type: str = 'patient') -> str:
        """
        Generate consistent pseudonym for an identifier.
        
        Args:
            identifier: Original identifier
            id_type: Type of identifier
            
        Returns:
            Pseudonymized identifier
        """
        # Create hash-based pseudonym
        hash_input = f"{self.hash_salt}:{id_type}:{identifier}"
        hash_obj = hashlib.sha256(hash_input.encode())
        hash_hex = hash_obj.hexdigest()[:12]
        
        return f"ANON_{id_type.upper()}_{hash_hex}"
    
    def anonymize_date(
        self,
        date: datetime,
        precision: str = 'year'
    ) -> datetime:
        """
        Anonymize date by reducing precision.
        
        Args:
            date: Original date
            precision: Level of precision ('year', 'month', 'day')
            
        Returns:
            Anonymized date
        """
        if precision == 'year':
            return datetime(date.year, 1, 1)
        elif precision == 'month':
            return datetime(date.year, date.month, 1)
        else:
            return date
    
    def anonymize_age(self, age: int, bin_size: int = 5) -> str:
        """
        Bin age for anonymization.
        
        Args:
            age: Patient age
            bin_size: Size of age bins
            
        Returns:
            Age range string
        """
        if age < 18:
            return "<18"
        elif age >= 90:
            return "90+"
        else:
            lower = (age // bin_size) * bin_size
            upper = lower + bin_size - 1
            return f"{lower}-{upper}"
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect potential PII in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected PII with type and location
        """
        detected = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                detected.append({
                    'type': pii_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return detected
    
    def k_anonymize(
        self,
        records: List[Dict[str, Any]],
        quasi_identifiers: List[str],
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Apply k-anonymity to dataset.
        
        Args:
            records: List of patient records
            quasi_identifiers: Fields that are quasi-identifiers
            k: Minimum group size
            
        Returns:
            K-anonymized records
        """
        # Simplified k-anonymity implementation
        # In production, use proper generalization hierarchies
        
        anonymized_records = []
        
        for record in records:
            anonymized = record.copy()
            
            # Generalize quasi-identifiers
            if 'age' in quasi_identifiers and 'age' in record:
                anonymized['age'] = self.anonymize_age(record['age'])
            
            if 'zip_code' in quasi_identifiers and 'zip_code' in record:
                # Keep only first 3 digits of ZIP
                anonymized['zip_code'] = record['zip_code'][:3] + "**"
            
            anonymized_records.append(anonymized)
        
        return anonymized_records
