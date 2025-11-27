"""Strategy selector for choosing appropriate model strategy."""

from typing import Dict, Any, List, Optional

from ..models.patient import PatientRecord
from .model_strategy import (
    ModelStrategy, PathologyStrategy, DeviceStrategy, 
    DomainStrategy, EnsembleStrategy
)


class StrategySelector:
    """
    Selects the appropriate model strategy based on patient record characteristics.
    Implements the Strategy pattern for swappable AI models.
    """
    
    def __init__(self):
        self.strategies: List[ModelStrategy] = []
        self.default_strategy: Optional[ModelStrategy] = None
        self.use_ensemble: bool = False
        
    def register_strategy(self, strategy: ModelStrategy):
        """Register a strategy for consideration."""
        self.strategies.append(strategy)
    
    def set_default_strategy(self, strategy: ModelStrategy):
        """Set default strategy when no specific strategy matches."""
        self.default_strategy = strategy
    
    def enable_ensemble(self, enabled: bool = True):
        """Enable ensemble mode to use multiple strategies."""
        self.use_ensemble = enabled
    
    def select_strategy(
        self,
        record: PatientRecord,
        context: Dict[str, Any]
    ) -> ModelStrategy:
        """
        Select the most appropriate strategy for the patient record.
        
        Args:
            record: Patient record to analyze
            context: Processing context
            
        Returns:
            Selected ModelStrategy instance
        """
        applicable_strategies = [
            strategy for strategy in self.strategies
            if strategy.can_handle(record, context)
        ]
        
        if not applicable_strategies:
            if self.default_strategy:
                return self.default_strategy
            raise ValueError("No applicable strategy found and no default strategy set")
        
        # If ensemble mode is enabled and multiple strategies apply, use ensemble
        if self.use_ensemble and len(applicable_strategies) > 1:
            return EnsembleStrategy(applicable_strategies)
        
        # Otherwise, select the most confident strategy
        # For now, just return the first applicable one
        # In production, could rank by confidence or specificity
        return applicable_strategies[0]
    
    def get_available_strategies(self) -> List[str]:
        """Get list of registered strategy names."""
        return [s.strategy_name for s in self.strategies]
    
    @classmethod
    def create_default_selector(cls) -> 'StrategySelector':
        """Create a selector with default strategies."""
        selector = cls()
        
        # Register domain strategies
        selector.register_strategy(DomainStrategy("cardiology"))
        selector.register_strategy(DomainStrategy("neurology"))
        selector.register_strategy(DomainStrategy("pulmonology"))
        selector.register_strategy(DomainStrategy("oncology"))
        selector.register_strategy(DomainStrategy("radiology"))
        
        # Register device strategies
        selector.register_strategy(DeviceStrategy("cardiac"))
        selector.register_strategy(DeviceStrategy("neurological"))
        selector.register_strategy(DeviceStrategy("respiratory"))
        
        # Register pathology strategies
        selector.register_strategy(PathologyStrategy("cancer"))
        selector.register_strategy(PathologyStrategy("tissue"))
        
        # Set a general domain strategy as default
        selector.set_default_strategy(DomainStrategy("general"))
        
        return selector
