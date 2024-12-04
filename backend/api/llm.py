# api/llm.py
from quart import Blueprint, request, jsonify
from api.utils import jwt_or_api_key_required

llm_blueprint = Blueprint('llm', __name__)

@llm_blueprint.route("/api/texts/rewrite", methods=["POST"])
@jwt_or_api_key_required(["admin", "user"])
async def rewrite():
    request_data = await request.get_json()
    return jsonify({"msg": "rewrite successful", "data": request_data}), 200