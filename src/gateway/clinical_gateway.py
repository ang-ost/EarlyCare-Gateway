"""Main Clinical Gateway implementation."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from ..models.patient import PatientRecord
from ..models.decision import DecisionSupport, UrgencyLevel
from .chain_handler import ChainHandler, ValidationHandler, EnrichmentHandler, TriageHandler
from ..strategy.strategy_selector import StrategySelector
from ..observer.monitoring import MonitoringSubject


class ClinicalGateway(MonitoringSubject):
    """
    Main gateway for routing clinical data through processing pipeline.
    Implements Chain of Responsibility pattern for data flow.
    """
    
    def __init__(self):
        super().__init__()
        self.request_count = 0
        self.chain_handlers: List[ChainHandler] = []
        self.strategy_selector: Optional[StrategySelector] = None
        
        # Set up default processing chain
        self._setup_default_chain()
        
        # Set up default strategy selector
        self._setup_default_strategy_selector()
    
    def _setup_default_chain(self):
        """Set up the default processing chain."""
        # Create handlers
        validation = ValidationHandler()
        enrichment = EnrichmentHandler()
        triage = TriageHandler()
        
        # Link handlers
        validation.set_next(enrichment).set_next(triage)
        
        # Store the chain (starting with first handler)
        self.chain_handlers = [validation, enrichment, triage]
    
    def _setup_default_strategy_selector(self):
        """Set up the default strategy selector."""
        try:
            self.strategy_selector = StrategySelector.create_default_selector()
            print(f"✅ Strategy selector initialized with {len(self.strategy_selector.strategies)} strategies")
            print(f"   Default strategy: {self.strategy_selector.default_strategy.strategy_name if self.strategy_selector.default_strategy else 'None'}")
        except Exception as e:
            print(f"❌ Failed to initialize strategy selector: {e}")
            self.strategy_selector = None
    
    def set_processing_chain(self, handlers: List[ChainHandler]):
        """
        Set a custom processing chain.
        
        Args:
            handlers: List of chain handlers in order
        """
        if not handlers:
            raise ValueError("At least one handler is required")
        
        # Link handlers
        for i in range(len(handlers) - 1):
            handlers[i].set_next(handlers[i + 1])
        
        self.chain_handlers = handlers
    
    def set_strategy_selector(self, selector: StrategySelector):
        """Set the strategy selector for model selection."""
        self.strategy_selector = selector
    
    def process_request(
        self,
        patient_record: PatientRecord,
        context: Optional[Dict[str, Any]] = None
    ) -> DecisionSupport:
        """
        Process a clinical request through the gateway.
        
        Args:
            patient_record: Patient record with clinical data
            context: Optional context dictionary for processing
            
        Returns:
            DecisionSupport object with diagnosis and recommendations
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Initialize context
        if context is None:
            context = {}
        context['request_id'] = request_id
        context['start_time'] = start_time
        
        # Notify observers - request started
        self.notify_observers('request_started', {
            'request_id': request_id,
            'patient_id': patient_record.patient.patient_id,
            'data_types': [d.data_type.value for d in patient_record.clinical_data]
        })
        
        try:
            # Run through processing chain
            if self.chain_handlers:
                processed_record = self.chain_handlers[0].handle(patient_record, context)
            else:
                processed_record = patient_record
            
            # Select and execute model strategy
            decision_support = self._execute_decision_support(processed_record, context)
            
            # Calculate total processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            decision_support.processing_time_ms = processing_time
            
            # Add triage information to decision support
            if 'triage' in context:
                decision_support.triage_score = context['triage']['score']
                triage_priority = context['triage']['priority']
                decision_support.urgency_level = UrgencyLevel[triage_priority.upper()]
            
            # Notify observers - request completed
            self.notify_observers('request_completed', {
                'request_id': request_id,
                'patient_id': processed_record.patient.patient_id,
                'processing_time_ms': processing_time,
                'diagnoses_count': len(decision_support.diagnoses),
                'urgency_level': decision_support.urgency_level.value
            })
            
            self.request_count += 1
            return decision_support
            
        except Exception as e:
            # Notify observers - request failed
            self.notify_observers('request_failed', {
                'request_id': request_id,
                'patient_id': patient_record.patient.patient_id,
                'error': str(e)
            })
            raise
    
    def _execute_decision_support(
        self,
        record: PatientRecord,
        context: Dict[str, Any]
    ) -> DecisionSupport:
        """
        Execute decision support using selected model strategy.
        
        Args:
            record: Processed patient record
            context: Processing context
            
        Returns:
            DecisionSupport object
        """
        request_id = context['request_id']
        
        # Create decision support object
        decision_support = DecisionSupport(
            request_id=request_id,
            patient_id=record.patient.patient_id,
            timestamp=datetime.now()
        )
        
        # Use strategy selector if available
        if self.strategy_selector:
            strategy = self.strategy_selector.select_strategy(record, context)
            decision_support = strategy.execute(record, decision_support, context)
            decision_support.models_used.append(strategy.strategy_name)
        else:
            # Default simple decision support (placeholder)
            decision_support.clinical_notes.append(
                "No model strategy configured - using default processing"
            )
        
        # Add processing metadata
        decision_support.metadata['context'] = {
            'validation': context.get('validation', {}),
            'enrichment': context.get('enrichment', {}),
            'triage': context.get('triage', {})
        }
        
        return decision_support
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get gateway statistics."""
        return {
            'total_requests': self.request_count,
            'chain_handlers': [h.handler_name for h in self.chain_handlers],
            'observers_count': len(self._observers)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on gateway components."""
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'chain_handlers': len(self.chain_handlers) > 0,
                'strategy_selector': self.strategy_selector is not None,
                'observers': len(self._observers)
            }
        }
        
        if len(self.chain_handlers) == 0:
            health['status'] = 'degraded'
            health['warnings'] = ['No chain handlers configured']
        
        return health
