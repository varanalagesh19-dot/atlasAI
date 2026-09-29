from .base import AIProvider

class MockProvider(AIProvider):
    """Mock provider for demo/testing"""
    
    def __init__(self):
        self.responses = {
            'hello': 'Hello! I\'m atlas_core07, your AI assistant. How can I help you today?',
            'hi': 'Hi there! What can I do for you?',
            'how are you': 'I\'m doing great, thanks for asking! Ready to help.',
            'what is atlas': 'atlas_core07 is an advanced AI chatbot platform built with React and Flask.',
            'help': 'I can assist you with various tasks. Ask me anything!',
            'default': 'That\'s an interesting question. In demo mode, I\'m providing pre-written responses. Connect a real AI provider for full capabilities!'
        }
    
    def generate(self, messages, model=None, temperature=0.7, max_tokens=2000):
        """Generate response from mock provider"""
        if not messages:
            return "Hello! How can I help?"
        
        last_message = messages[-1].get('content', '').lower()
        
        for key, response in self.responses.items():
            if key in last_message:
                return response
        
        return self.responses['default']
    
    def get_models(self):
        """Return available models"""
        return [
            {'id': 'atlas_smart', 'name': 'atlas Smart (Demo)'},
            {'id': 'atlas_fast', 'name': 'atlas Fast (Demo)'},
            {'id': 'atlas_creative', 'name': 'atlas Creative (Demo)'}
        ]
    
    @property
    def is_available(self):
        """Mock provider is always available"""
        return True
