# api/llm.py
from quart import Blueprint, request, jsonify, current_app, Response
from api.utils import jwt_or_api_key_required
from llm.llm import read_file_contents, process_text_before_rewriting, process_text_after_rewriting
from config import llm_cache_store, REDIS_CACHE_TTL
import json
import hashlib
from bs4 import BeautifulSoup
import os

llm_blueprint = Blueprint('llm', __name__)

RAY_SERVE_URL = os.getenv("RAY_SERVE_URL", "http://localhost:8000")
SCHRIJFASSISTENT_MODELFILE = "llm/Modelfile_schrijfassistent"
STIJLASSISTENT_MODELFILE = "llm/Modelfile_stijlassistent"
HOST = "http://ollama:11434"

async def initialize_models():
    """
    Preload models on Ollama using the shared aiohttp.ClientSession.
    """
    try:
        async with current_app.aiohttp_session.post(
            f"{HOST}/api/create",
            json={
                "model": "schrijfassistent",
                "modelfile": read_file_contents(SCHRIJFASSISTENT_MODELFILE),
            }
        ) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to initialize 'schrijfassistent': {response.status}")

        async with current_app.aiohttp_session.post(
            f"{HOST}/api/create",
            json={
                "model": "stijlassistent",
                "modelfile": read_file_contents(STIJLASSISTENT_MODELFILE),
            }
        ) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to initialize 'stijlassistent': {response.status}")

        current_app.logger.info("Models 'schrijfassistent' and 'stijlassistent' initialized successfully.")
    except Exception as e:
        current_app.logger.error(f"Model initialization failed: {e}")

def generate_cache_key(sentence: str) -> str:
    """
    Generate a unique cache key for a given sentence.
    """
    return hashlib.sha256(sentence.encode()).hexdigest()

async def fetch_response(session, host, model, prompt, stream=False):
    """Helper function to call the API and process the response."""
    async with session.post(
        f"{host}/api/generate",
        json={"model": model, "prompt": prompt, "stream": stream}
    ) as response:
        if response.status != 200:
            raise ValueError(f"Failed to call '{model}': {response.status}")
        
        if stream:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line:
                    try:
                        data = json.loads(line)
                        yield data.get("response", "")
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON from {model}: {line}. Error: {e}")
        else:
            result = ""
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line:
                    try:
                        data = json.loads(line)
                        result += data.get("response", "")
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON from {model}: {line}. Error: {e}")
            yield result

@llm_blueprint.route("/api/model/rewrite", methods=["POST"])
async def rewrite():
    """
    Handle requests to rewrite text using the LLM with optional streaming.
    """
    try:
        # Get request data
        request_data = await request.get_json()
        text = request_data.get("text")
        user_prompt = request_data.get("user_prompt")
        regenerate = request_data.get("regenerate", False)
        stream = request_data.get("stream", False)

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Generate a cache key based on text and user_prompt
        cache_key = generate_cache_key(f"{text}_{user_prompt or ''}")

        session = current_app.aiohttp_session

        # If streaming is disabled, check the cache
        if not stream and not regenerate:
            cached_response = llm_cache_store.get(cache_key)
            if cached_response:
                return jsonify({"msg": "Rewrite successful", "data": json.loads(cached_response)}), 200

        # Fetch the response from the first model
        rewritten_response = ""
        async for chunk in fetch_response(session, HOST, "schrijfassistent", text):
            rewritten_response += chunk

        # Handle streaming for the second model
        if stream:
            async def stream_response():
                async for chunk in fetch_response(session, HOST, "stijlassistent", rewritten_response, stream=True):
                    yield chunk

            # Skip caching if streaming is enabled
            return Response(stream_response(), content_type="text/plain")
        else:
            # Fetch the full response from the second model
            styled_response = ""
            async for chunk in fetch_response(session, HOST, "stijlassistent", rewritten_response):
                styled_response += chunk

            # Cache the response
            llm_cache_store.set(cache_key, json.dumps(styled_response), ex=REDIS_CACHE_TTL)
            return jsonify({"msg": "Rewrite successful", "data": styled_response}), 200

    except Exception as e:
        current_app.logger.error(f"Rewrite failed with error: {e}")
        return jsonify({"error": "Rewrite failed"}), 500