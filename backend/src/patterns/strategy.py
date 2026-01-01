"""
Strategy Pattern Implementation
Allows selection of different AI models/providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AIModelStrategy(ABC):
    """Abstract strategy for AI model selection"""
    
    @abstractmethod
    def generate_diagnosis(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate diagnosis using specific AI model"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name"""
        pass


class GeminiStrategy(AIModelStrategy):
    """Google Gemini AI strategy"""
    
    def __init__(self, ai_instance):
        self.ai = ai_instance
    
    def generate_diagnosis(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Using Gemini model for diagnosis")
        return self.ai.generate_diagnosis(patient_data)
    
    def get_model_name(self) -> str:
        return "Google Gemini"


class OpenAIStrategy(AIModelStrategy):
    """OpenAI GPT strategy (placeholder for future implementation)"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def generate_diagnosis(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("OpenAI strategy not yet implemented")
        return {
            "error": "OpenAI integration not yet available",
            "model": "OpenAI GPT"
        }
    
    def get_model_name(self) -> str:
        return "OpenAI GPT"


class ClaudeStrategy(AIModelStrategy):
    """Anthropic Claude strategy (placeholder for future implementation)"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def generate_diagnosis(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Claude strategy not yet implemented")
        return {
            "error": "Claude integration not yet available",
            "model": "Anthropic Claude"
        }
    
    def get_model_name(self) -> str:
        return "Anthropic Claude"


class AIModelContext:
    """Context that uses an AI model strategy"""
    
    def __init__(self, strategy: AIModelStrategy = None):
        self._strategy = strategy
    
    def set_strategy(self, strategy: AIModelStrategy):
        """Change the AI model strategy at runtime"""
        logger.info(f"Switching to {strategy.get_model_name()}")
        self._strategy = strategy
    
    def generate_diagnosis(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate diagnosis using the current strategy"""
        if not self._strategy:
            raise ValueError("No AI strategy set")
        
        return self._strategy.generate_diagnosis(patient_data)
    
    def get_current_model(self) -> str:
        """Get the name of the current model"""
        return self._strategy.get_model_name() if self._strategy else "None"
