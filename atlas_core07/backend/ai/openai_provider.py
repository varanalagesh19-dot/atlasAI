import os
from .base import AIProvider

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        
        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
    
    def generate(self, messages, model='gpt-3.5-turbo', temperature=0.7, max_tokens=2000):
        """Generate response using OpenAI"""
        if not self.is_available:
            raise Exception("OpenAI API key not configured")
        
        try:
            response = self.client.chat.completions.create(
                model=model or 'gpt-3.5-turbo',
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI error: {str(e)}")
    
    def get_models(self):
        """Return available OpenAI models"""
        return [
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo'},
            {'id': 'gpt-4', 'name': 'GPT-4'},
            {'id': 'gpt-4-turbo-preview', 'name': 'GPT-4 Turbo'}
        ]
    
    @property
    def is_available(self):
        """Check if OpenAI is configured"""
        return self.api_key is not None and self.client is not None
