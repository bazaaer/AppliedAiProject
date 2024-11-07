# api/model.py
from quart import Blueprint, request, jsonify
from api.utils import api_key_required

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api', methods=['GET'])
async def index():
    return 'Klopta API is running!'

@api_blueprint.route("/api/rewrite", methods=["POST"])
@api_key_required
async def rewrite():
    # Your rewrite logic here
    return jsonify({"msg": "Rewrite successful"}), 200