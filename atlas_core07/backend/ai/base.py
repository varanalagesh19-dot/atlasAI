from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Base class for all AI providers"""
    
    @abstractmethod
    def generate(self, messages, model=None, temperature=0.7, max_tokens=2000):
        """Generate AI response"""
        pass
    
    @abstractmethod
    def get_models(self):
        """Get list of available models"""
        pass
    
    @property
    @abstractmethod
    def is_available(self):
        """Check if provider is configured"""
        pass
    
    @property
    def provider_name(self):
        """Get provider name"""
        return self.__class__.__name__
