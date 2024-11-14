# api/model.py
from quart import Blueprint, request, jsonify
from api.utils import jwt_or_api_key_required
from markdown2 import markdown
from html2text import html2text

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

    # Set default for 'selection' if not provided
    selection = request_data.get("selection", False)

    # Convert 'text' from HTML to Markdown
    html_text = request_data.get("text", "")
    markdown_text = html2text(html_text) if html_text else ""

    processed_html = markdown(markdown_text)

    return jsonify({
        "msg": "score successful",
        "data": {
            "text": processed_html,
            "selection": selection
        }
    }), 200

@model_blueprint.route("/api/rewrite", methods=["POST"])
@jwt_or_api_key_required(["admin", "user"])
async def rewrite():
    request_data = await request.get_json()
    return jsonify({"msg": "rewrite successful", "data": request_data}), 200