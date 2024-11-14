# api/model.py
from quart import Blueprint, request, jsonify
from api.utils import jwt_or_api_key_required
from checket.grouper import SentenceGrouper
import re

grouper = SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.75)

model_blueprint = Blueprint('model', __name__)

@model_blueprint.route('/api', methods=['GET'])
async def index():
    """
    Check if the API is running.
    This asynchronous function returns a JSON response to indicate that the API is running.
    Returns:
        Response: A JSON response with a message indicating that the API is running.
    """

    return jsonify({"msg": "Klopta API is running"}), 200

@model_blueprint.route("/api/score", methods=["POST"])
# @jwt_or_api_key_required(["admin", "user"])
async def score():
    request_data = await request.get_json()

    # Extract 'text' and remove HTML tags
    html_text = request_data.get("text", "")
    plain_text = re.sub(r'<[^>]*>', '', html_text) if html_text else ""
    print(plain_text)

    result = grouper.group_consecutive_similar_sentences(plain_text)

    response = []
    for sentence, group_index in result:
        response.append({"sentence": sentence, "group": group_index})

    return jsonify(response), 200

@model_blueprint.route("/api/rewrite", methods=["POST"])
@jwt_or_api_key_required(["admin", "user"])
async def rewrite():
    request_data = await request.get_json()
    return jsonify({"msg": "rewrite successful", "data": request_data}), 200