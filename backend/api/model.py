from quart import Blueprint, request, jsonify, current_app, Response
import aiohttp
import os
from bs4 import BeautifulSoup
from api.utils import jwt_or_api_key_required, jwt_role_required

model_blueprint = Blueprint('model', __name__)

RAY_SERVE_URL = os.getenv("RAY_SERVE_URL", "http://localhost:8000")
RAY_DASHBOARD_URL = os.getenv("RAY_DASHBOARD_URL", "http://localhost:8265")

@model_blueprint.route('/api', methods=['GET'])
async def index():
    """
    Check if the API is running.
    """
    return jsonify({"msg": "Klopta API is running"}), 200

@model_blueprint.route("/api/texts/score", methods=["POST"])
async def score():
    """
    Endpoint to score texts using Ray Serve.
    """
    try:
        request_data = await request.get_json()

        if not isinstance(request_data, dict):
            return jsonify({"error": "Invalid input: JSON object expected"}), 400

        text_input = request_data.get("text", None)

        # Validate the input
        if isinstance(text_input, str):
            texts = [text_input.strip()]  # Wrap a single string in a list
        elif isinstance(text_input, list) and all(isinstance(t, str) and t.strip() for t in text_input):
            texts = [t.strip() for t in text_input]  # Clean and process the list
        else:
            return jsonify({
                "error": "Invalid input: 'text' must be a non-empty string or a list of non-empty strings"
            }), 400

        # Clean each text by removing HTML tags
        cleaned_texts = []
        for text in texts:
            soup = BeautifulSoup(text, "html.parser")
            cleaned_text = soup.get_text(separator=" ").strip()
            if not cleaned_text:
                return jsonify({
                    "error": "One or more inputs become empty after removing HTML tags"
                }), 400
            cleaned_texts.append(cleaned_text)

        session = current_app.aiohttp_session
        try:
            async with session.post(f"{RAY_SERVE_URL}", json={"text": cleaned_texts}) as response:
                if response.status != 200:
                    return jsonify({
                        "error": "Error from Ray Serve",
                        "details": await response.text()
                    }), response.status

                ray_response = await response.json()
                return jsonify(ray_response)
        except aiohttp.ClientError as e:
            return jsonify({
                "error": "Failed to connect to Ray Serve",
                "details": str(e)
            }), 500

    except Exception as e:
        return jsonify({
            "error": "Invalid request payload",
            "details": str(e)
        }), 400


@model_blueprint.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
# @jwt_role_required(["admin"])
async def proxy_dashboard(path):
    """
    Proxy route for the Ray dashboard API and dashboard paths.
    """
    session = current_app.aiohttp_session
    is_dashboard_path = path.startswith("dashboard")
    base_url = RAY_DASHBOARD_URL if is_dashboard_path else f"{RAY_DASHBOARD_URL}/{path}"
    
    url = f"{RAY_DASHBOARD_URL}/{path}" if is_dashboard_path else base_url
    try:
        async with session.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            params=request.args,
            data=await request.get_data()
        ) as response:
            headers = {key: value for key, value in response.headers.items() if key.lower() != 'transfer-encoding'}
            body = await response.read()
            return Response(body, status=response.status, headers=headers)
    except aiohttp.ClientError as e:
        return jsonify({"error": f"Failed to fetch Ray API endpoint: {path}", "details": str(e)}), 502


@model_blueprint.route('/api/dashboard', methods=['GET'])
# @jwt_role_required(["admin"])
async def proxy_dashboard_root():
    """
    Proxy route for the root of the Ray dashboard.
    """
    session = current_app.aiohttp_session
    try:
        async with session.get(RAY_DASHBOARD_URL) as response:
            headers = {key: value for key, value in response.headers.items() if key.lower() != 'transfer-encoding'}
            body = await response.read()
            return Response(body, status=response.status, headers=headers)
    except aiohttp.ClientError as e:
        return jsonify({"error": "Failed to connect to Ray Dashboard", "details": str(e)}), 502