from flask import Blueprint, jsonify
from services.ai_service import get_ai_service

models_bp = Blueprint('models', __name__, url_prefix='/api')

@models_bp.route('/models', methods=['GET'])
def get_models():
    """Get available AI models"""
    try:
        ai_service = get_ai_service()
        models = ai_service.get_models()
        
        return jsonify({
            'models': models,
            'provider': ai_service.get_provider_name()
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error fetching models: {str(e)}'}), 500
