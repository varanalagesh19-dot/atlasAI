from flask import Blueprint, request, jsonify
from database.db import *

conversations_bp = Blueprint('conversations', __name__, url_prefix='/api')

@conversations_bp.route('/conversations', methods=['GET'])
def get_conversations_list():
    """Get all conversations"""
    try:
        convs = get_conversations()
        for conv in convs:
            conv['messages'] = []
        return jsonify(convs), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversations_bp.route('/conversations', methods=['POST'])
def create_new_conversation():
    """Create new conversation"""
    try:
        data = request.get_json()
        title = data.get('title', 'New Conversation')
        model = data.get('model', 'atlas_smart')
        
        conv_id = create_conversation(title, model)
        conv = get_conversation(conv_id)
        
        return jsonify(conv), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversations_bp.route('/conversations/<conv_id>', methods=['GET'])
def get_conv(conv_id):
    """Get specific conversation"""
    try:
        conv = get_conversation(conv_id)
        if not conv:
            return jsonify({'error': 'Conversation not found'}), 404
        return jsonify(conv), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversations_bp.route('/conversations/<conv_id>', methods=['PUT'])
def update_conv(conv_id):
    """Update conversation"""
    try:
        data = request.get_json()
        update_conversation(conv_id, 
                          title=data.get('title'),
                          model=data.get('model'),
                          pinned=data.get('pinned'))
        conv = get_conversation(conv_id)
        return jsonify(conv), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversations_bp.route('/conversations/<conv_id>', methods=['DELETE'])
def delete_conv(conv_id):
    """Delete conversation"""
    try:
        delete_conversation(conv_id)
        return jsonify({'message': 'Conversation deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversations_bp.route('/conversations/<conv_id>/messages', methods=['POST'])
def add_msg(conv_id):
    """Add message to conversation"""
    try:
        data = request.get_json()
        role = data.get('role')
        content = data.get('content')
        
        if not role or not content:
            return jsonify({'error': 'Missing required fields'}), 400
        
        msg = add_message(conv_id, role, content)
        return jsonify(msg), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@conversations_bp.route('/conversations/search', methods=['GET'])
def search_conv():
    """Search conversations"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([]), 200
        
        results = search_conversations(query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
