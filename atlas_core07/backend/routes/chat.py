from flask import Blueprint, request, jsonify
from services.ai_service import get_ai_service

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Generate AI response"""
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({'error': 'Missing messages field'}), 400
        
        messages = data.get('messages', [])
        model = data.get('model')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2000)
        
        ai_service = get_ai_service()
        response = ai_service.generate(messages, model, temperature, max_tokens)
        
        return jsonify({
            'content': response,
            'model': model or 'default',
            'provider': ai_service.get_provider_name()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'AI generation error: {str(e)}'}), 500
