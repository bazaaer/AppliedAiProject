# backend/api/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

# Create a blueprint
api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api', methods=['GET'])
def index():
    return 'Klopta API is running!'


@api_blueprint.route('/api/rewrite', methods=['POST'])
@jwt_required()
def rewrite_text():
    data = request.get_json()
    user_text = data.get('text', '')

    rewritten_text = "this is a rewritten text"

    if not user_text:
        return jsonify({'error': 'No text provided'}), 400

    try:

        return jsonify({'rewritten_text': rewritten_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
