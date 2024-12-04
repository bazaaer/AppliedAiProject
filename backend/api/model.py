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
# @jwt_or_api_key_required(["admin", "user"])
async def score():
    """
    Endpoint to score texts using Ray Serve.
    """
    try:
        request_data = await request.get_json()

        if not isinstance(request_data, dict):
            return jsonify({"error": "Invalid input: JSON object expected"}), 400

        html_text = request_data.get("text", None)
        if not isinstance(html_text, str) or not html_text.strip():
            return jsonify({"error": "Invalid input: 'text' must be a non-empty string"}), 400

        soup = BeautifulSoup(html_text, "html.parser")
        cleaned_text = soup.get_text(separator=" ").strip()

        if not cleaned_text:
            return jsonify({"error": "Input text becomes empty after removing HTML tags"}), 400

        session = current_app.aiohttp_session
        try:
            async with session.post(f"{RAY_SERVE_URL}/pipeline", json={"text": cleaned_text}) as response:
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