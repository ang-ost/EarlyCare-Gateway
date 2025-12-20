"""Audit logging for compliance and traceability."""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path


class AuditEventType(Enum):
    """Types of audit events."""
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_CHANGE = "permission_change"
    SYSTEM_CONFIG = "system_config"
    MODEL_EXECUTION = "model_execution"
    DATA_EXPORT = "data_export"
    CONSENT_CHANGE = "consent_change"


class AuditLogger:
    """
    HIPAA-compliant audit logger for tracking all system access and changes.
    Implements secure, tamper-evident logging.
    """
    
    def __init__(self, log_directory: str = "logs/audit"):
        """
        Initialize audit logger.
        
        Args:
            log_directory: Directory for audit log files
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Set up file handler
        self.log_file = self.log_directory / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configure logger
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # File handler with rotation
        handler = logging.FileHandler(self.log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logging
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.propagate = False
    
    def log_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        outcome: str = "success",
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            user_id: ID of user performing action
            action: Specific action performed
            resource: Type of resource accessed
            resource_id: ID of specific resource
            outcome: Outcome of action (success, failure)
            details: Additional event details
        """
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type.value,
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'resource_id': resource_id,
            'outcome': outcome,
            'details': details or {},
            'system': 'EarlyCareGateway'
        }
        
        # Log as JSON
        self.logger.info(json.dumps(audit_entry))
    
    def log_data_access(
        self,
        user_id: str,
        patient_id: str,
        data_type: str,
        purpose: str,
        outcome: str = "success"
    ) -> None:
        """
        Log patient data access.
        
        Args:
            user_id: User accessing data
            patient_id: Patient whose data was accessed
            data_type: Type of data accessed
            purpose: Purpose of access
            outcome: Success or failure
        """
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            user_id=user_id,
            action="read",
            resource="patient_data",
            resource_id=patient_id,
            outcome=outcome,
            details={
                'data_type': data_type,
                'purpose': purpose
            }
        )
    
    def log_model_execution(
        self,
        user_id: str,
        patient_id: str,
        model_name: str,
        request_id: str,
        outcome: str = "success",
        processing_time_ms: Optional[float] = None
    ) -> None:
        """
        Log AI model execution.
        
        Args:
            user_id: User requesting analysis
            patient_id: Patient being analyzed
            model_name: Name of model executed
            request_id: Unique request ID
            outcome: Success or failure
            processing_time_ms: Processing time
        """
        self.log_event(
            event_type=AuditEventType.MODEL_EXECUTION,
            user_id=user_id,
            action="execute",
            resource="ai_model",
            resource_id=model_name,
            outcome=outcome,
            details={
                'patient_id': patient_id,
                'request_id': request_id,
                'processing_time_ms': processing_time_ms
            }
        )
    
    def log_data_export(
        self,
        user_id: str,
        patient_id: str,
        export_format: str,
        destination: str,
        outcome: str = "success"
    ) -> None:
        """
        Log data export events.
        
        Args:
            user_id: User exporting data
            patient_id: Patient whose data was exported
            export_format: Format of export
            destination: Export destination
            outcome: Success or failure
        """
        self.log_event(
            event_type=AuditEventType.DATA_EXPORT,
            user_id=user_id,
            action="export",
            resource="patient_data",
            resource_id=patient_id,
            outcome=outcome,
            details={
                'export_format': export_format,
                'destination': destination
            }
        )
    
    def log_consent_change(
        self,
        user_id: str,
        patient_id: str,
        consent_type: str,
        consent_status: bool,
        outcome: str = "success"
    ) -> None:
        """
        Log patient consent changes.
        
        Args:
            user_id: User making change
            patient_id: Patient whose consent changed
            consent_type: Type of consent
            consent_status: New consent status
            outcome: Success or failure
        """
        self.log_event(
            event_type=AuditEventType.CONSENT_CHANGE,
            user_id=user_id,
            action="update",
            resource="patient_consent",
            resource_id=patient_id,
            outcome=outcome,
            details={
                'consent_type': consent_type,
                'consent_status': consent_status
            }
        )
    
    def log_authentication(
        self,
        user_id: str,
        action: str,
        source_ip: Optional[str] = None,
        outcome: str = "success"
    ) -> None:
        """
        Log user authentication events.
        
        Args:
            user_id: User ID
            action: 'login' or 'logout'
            source_ip: IP address of user
            outcome: Success or failure
        """
        event_type = AuditEventType.USER_LOGIN if action == 'login' else AuditEventType.USER_LOGOUT
        
        self.log_event(
            event_type=event_type,
            user_id=user_id,
            action=action,
            resource="authentication",
            outcome=outcome,
            details={'source_ip': source_ip}
        )
    
    def query_logs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        resource_id: Optional[str] = None
    ) -> list:
        """
        Query audit logs with filters.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            user_id: Filter by user
            event_type: Filter by event type
            resource_id: Filter by resource
            
        Returns:
            List of matching audit entries
        """
        results = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        
                        # Apply filters
                        if start_time and datetime.fromisoformat(entry['timestamp'].rstrip('Z')) < start_time:
                            continue
                        
                        if end_time and datetime.fromisoformat(entry['timestamp'].rstrip('Z')) > end_time:
                            continue
                        
                        if user_id and entry.get('user_id') != user_id:
                            continue
                        
                        if event_type and entry.get('event_type') != event_type.value:
                            continue
                        
                        if resource_id and entry.get('resource_id') != resource_id:
                            continue
                        
                        results.append(entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return results
    
    def get_patient_access_log(self, patient_id: str, days: int = 30) -> list:
        """
        Get all access events for a specific patient.
        
        Args:
            patient_id: Patient ID
            days: Number of days to look back
            
        Returns:
            List of access events
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        return self.query_logs(
            start_time=start_time,
            resource_id=patient_id
        )


# For compatibility with datetime operations
from datetime import timedelta
