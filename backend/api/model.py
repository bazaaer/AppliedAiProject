# api/model.py
from quart import Blueprint, request, jsonify

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api', methods=['GET'])
async def index():
    return 'Klopta API is running!'

@api_blueprint.route('/api/rewrite', methods=['POST'])
async def rewrite():
    data = await request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'message': 'Text is required'}), 400
    return jsonify({'text': text[::-1]}), 200