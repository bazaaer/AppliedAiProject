# api/model.py
from quart import Blueprint, request, jsonify
from api.utils import jwt_or_api_key_required
from checket.grouper import SentenceGrouper
from checket.checker import SimilarityEvaluator
import re

grouper = SentenceGrouper(model="nl_core_news_md", similarity_threshold=0.75)

training_embeddings_path = "checket/embeddings.pt"
similarity_evaluator = SimilarityEvaluator(training_embeddings_path)

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

@model_blueprint.route("/api/texts/score", methods=["POST"])
# @jwt_or_api_key_required(["admin", "user"])
async def score():
    request_data = await request.get_json()

    # Extract 'text' and remove HTML tags
    html_text = request_data.get("text", "")
    plain_text = re.sub(r'<[^>]*>', '', html_text) if html_text else ""

    result = grouper.group_consecutive_similar_sentences(plain_text)

    response = []
    for sentence, group_index in result:
        score = similarity_evaluator.topk_mean_similarity_score(sentence,k=8)
        response.append({"sentence": sentence, "group": group_index, "score": score})

    return jsonify(response), 200

@model_blueprint.route("/api/texts/rewrite", methods=["POST"])
@jwt_or_api_key_required(["admin", "user"])
async def rewrite():
    request_data = await request.get_json()
    return jsonify({"msg": "rewrite successful", "data": request_data}), 200