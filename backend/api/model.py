# api/model.py
from quart import Blueprint, request, jsonify
from api.utils import jwt_or_api_key_required
from bs4 import BeautifulSoup
import aiohttp
import os

model_blueprint = Blueprint('model', __name__)

RAY_SERVE_BASE_URL = os.getenv("RAY_SERVE_BASE_URL", "http://localhost:8000")
print(f"RAY_SERVE_BASE_URL: {RAY_SERVE_BASE_URL}")

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
async def score():
    # Parse the request data
    request_data = await request.get_json()
    html_text = request_data.get("text", "")

    if not html_text:
        return jsonify({"error": "No text provided in the request"}), 400

    # Parse the HTML and extract plain text
    soup = BeautifulSoup(html_text, "html.parser")
    plain_text = soup.get_text()

    # Make asynchronous HTTP requests to Ray Serve endpoints
    async with aiohttp.ClientSession() as session:
        try:
            # Call the Sentence Grouper endpoint
            async with session.post(
                f"{RAY_SERVE_BASE_URL}/grouper",
                json={"text": plain_text},
                headers={"Content-Type": "application/json"}
            ) as grouper_response:
                if grouper_response.status != 200:
                    error_text = await grouper_response.text()
                    return jsonify({"error": "Grouper failed", "details": error_text}), 500
                grouper_data = await grouper_response.json()

            # Extract grouped sentences
            grouped_sentences = [group[0] for group in grouper_data["result"]]

            # Call the Similarity Evaluator endpoint
            async with session.post(
                f"{RAY_SERVE_BASE_URL}/evaluator",
                json={"sentences": grouped_sentences},
                headers={"Content-Type": "application/json"}
            ) as evaluator_response:
                if evaluator_response.status != 200:
                    error_text = await evaluator_response.text()
                    return jsonify({"error": "Evaluator failed", "details": error_text}), 500
                evaluator_data = await evaluator_response.json()

        except aiohttp.ClientError as e:
            return jsonify({"error": "HTTP request failed", "details": str(e)}), 500

    # Reapply HTML tags to the processed sentences
    response = []
    for group_index, (sentence, score_data) in enumerate(zip(grouped_sentences, evaluator_data["result"])):
        # Find the exact tag containing the sentence, matching sentence boundaries
        for tag in soup.find_all():
            tag_text = tag.get_text()
            # Look for exact sentence matches
            if sentence in tag_text:
                start_index = tag_text.find(sentence)
                end_index = start_index + len(sentence)
                # Extract the matched HTML fragment
                original_html = str(tag)[start_index:end_index]
                break
        else:
            # Use plain text if no match is found
            original_html = sentence

        # Append the original HTML with group and score information
        response.append({
            "sentence": original_html,
            "group": group_index,
            "score": score_data.get("score", 0)
        })

    return jsonify({"result": response}), 200

@model_blueprint.route("/api/texts/rewrite", methods=["POST"])
@jwt_or_api_key_required(["admin", "user"])
async def rewrite():
    request_data = await request.get_json()
    return jsonify({"msg": "rewrite successful", "data": request_data}), 200