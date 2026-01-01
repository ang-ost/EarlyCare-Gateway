"""
Observer Pattern Implementation
Monitors system events and metrics in production
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Observer(ABC):
    """Abstract observer interface"""
    
    @abstractmethod
    def update(self, event: Dict[str, Any]):
        """Receive update from subject"""
        pass


class Subject:
    """Subject that notifies observers of events"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer):
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"Observer attached: {observer.__class__.__name__}")
    
    def detach(self, observer: Observer):
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"Observer detached: {observer.__class__.__name__}")
    
    def notify(self, event: Dict[str, Any]):
        """Notify all observers of an event"""
        for observer in self._observers:
            observer.update(event)


class AuditLogObserver(Observer):
    """Observer that logs events to audit trail"""
    
    def __init__(self, db_collection=None):
        self.db_collection = db_collection
    
    def update(self, event: Dict[str, Any]):
        logger.info(f"Audit Log: {event.get('event_type', 'unknown')} - {event.get('description', '')}")
        
        if self.db_collection:
            audit_entry = {
                'timestamp': datetime.now(),
                'event_type': event.get('event_type'),
                'user_id': event.get('user_id'),
                'description': event.get('description'),
                'metadata': event.get('metadata', {})
            }
            try:
                self.db_collection.insert_one(audit_entry)
            except Exception as e:
                logger.error(f"Failed to write audit log: {e}")


class MetricsObserver(Observer):
    """Observer that tracks system metrics"""
    
    def __init__(self):
        self.metrics = {
            'total_events': 0,
            'events_by_type': {},
            'last_event_time': None
        }
    
    def update(self, event: Dict[str, Any]):
        self.metrics['total_events'] += 1
        self.metrics['last_event_time'] = datetime.now()
        
        event_type = event.get('event_type', 'unknown')
        self.metrics['events_by_type'][event_type] = self.metrics['events_by_type'].get(event_type, 0) + 1
        
        logger.info(f"Metrics: Total events = {self.metrics['total_events']}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()


class AlertObserver(Observer):
    """Observer that sends alerts for critical events"""
    
    def __init__(self, alert_threshold: int = 5):
        self.alert_threshold = alert_threshold
        self.error_count = 0
    
    def update(self, event: Dict[str, Any]):
        if event.get('severity') == 'error' or event.get('event_type') == 'error':
            self.error_count += 1
            
            if self.error_count >= self.alert_threshold:
                logger.warning(f"ALERT: Error threshold reached ({self.error_count} errors)")
                self.error_count = 0


class MonitoringSystem(Subject):
    """Central monitoring system using observer pattern"""
    
    def __init__(self, db=None):
        super().__init__()
        self.audit_observer = AuditLogObserver(db.audit_logs if db else None)
        self.metrics_observer = MetricsObserver()
        self.alert_observer = AlertObserver()
        
        self.attach(self.audit_observer)
        self.attach(self.metrics_observer)
        self.attach(self.alert_observer)
    
    def log_event(self, event_type: str, description: str, user_id: str = None, 
                  severity: str = 'info', metadata: Dict[str, Any] = None):
        """Log an event and notify observers"""
        event = {
            'event_type': event_type,
            'description': description,
            'user_id': user_id,
            'severity': severity,
            'metadata': metadata or {},
            'timestamp': datetime.now()
        }
        self.notify(event)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return self.metrics_observer.get_metrics()
