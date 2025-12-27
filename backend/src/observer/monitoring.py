"""Observer pattern implementation for monitoring and event handling."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime


class Observer(ABC):
    """Abstract observer for monitoring events."""
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]):
        """
        Called when an observed event occurs.
        
        Args:
            event_type: Type of event that occurred
            data: Event data
        """
        pass


class MonitoringSubject:
    """Subject that can be observed. Implements Observable pattern."""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach_observer(self, observer: Observer):
        """Attach an observer to receive notifications."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach_observer(self, observer: Observer):
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event_type: str, data: Dict[str, Any]):
        """Notify all observers of an event."""
        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                # Log error but continue notifying other observers
                print(f"Error notifying observer {observer.__class__.__name__}: {e}")
