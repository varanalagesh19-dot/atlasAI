import os
from ai.mock import MockProvider
from ai.openai_provider import OpenAIProvider

class AIService:
    """Service for managing AI providers"""
    
    def __init__(self):
        self.provider_name = os.getenv('AI_PROVIDER', 'mock').lower()
        self.provider = self._init_provider()
    
    def _init_provider(self):
        """Initialize the configured provider"""
        if self.provider_name == 'openai':
            provider = OpenAIProvider()
            if provider.is_available:
                return provider
        
        if self.provider_name == 'gemini':
            try:
                from ai.gemini_provider import GeminiProvider
                provider = GeminiProvider()
                if provider.is_available:
                    return provider
            except ImportError:
                pass
        
        if self.provider_name == 'anthropic':
            try:
                from ai.anthropic_provider import AnthropicProvider
                provider = AnthropicProvider()
                if provider.is_available:
                    return provider
            except ImportError:
                pass
        
        # Default to mock
        return MockProvider()
    
    def generate(self, messages, model=None, temperature=0.7, max_tokens=2000):
        """Generate AI response"""
        return self.provider.generate(messages, model, temperature, max_tokens)
    
    def get_models(self):
        """Get available models"""
        return self.provider.get_models()
    
    def get_provider_name(self):
        """Get active provider name"""
        return self.provider.provider_name

# Singleton instance
_ai_service = None

def get_ai_service():
    """Get AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
