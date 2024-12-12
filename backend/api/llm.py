# api/llm.py
from quart import Blueprint, request, jsonify, current_app
from api.utils import jwt_or_api_key_required
from llm.llm import read_file_contents, write_sentence
from config import llm_cache_store, REDIS_CACHE_TTL
import json
import hashlib

llm_blueprint = Blueprint('llm', __name__)

SCHRIJFASSISTENT_MODELFILE = "llm/Modelfile_schrijfassistent"
STIJLASSISTENT_MODELFILE = "llm/Modelfile_stijlassistent"
HOST = "http://ollama:11434"

async def initialize_models():
    """
    Preload models on Ollama using the shared aiohttp.ClientSession.
    """
    try:
        print("Initializing models...")
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

@llm_blueprint.route("/api/model/rewrite", methods=["POST"])
@jwt_or_api_key_required(["admin", "user"])
async def rewrite():
    """
    Handle requests to rewrite sentences using the LLM with caching.
    """
    try:
        # Get request data
        request_data = await request.get_json()
        sentence = request_data.get("sentence")
        if not sentence:
            return jsonify({"error": "No sentence provided"}), 400

        # Generate a cache key
        cache_key = generate_cache_key(sentence)

        # Check Redis cache for an existing response
        cached_response = llm_cache_store.get(cache_key)
        if cached_response:
            return jsonify({"msg": "Rewrite successful", "data": json.loads(cached_response)}), 200

        # Call the asynchronous write_sentence function
        response = await write_sentence(
            session=current_app.aiohttp_session,
            host=HOST,
            sentence=sentence
        )

        # Cache the response
        llm_cache_store.set(cache_key, json.dumps(response), ex=REDIS_CACHE_TTL)

        return jsonify({"msg": "Rewrite successful", "data": response}), 200
    except Exception as e:
        current_app.logger.error(f"Rewrite failed with error: {e}")
        return jsonify({"error": "Rewrite failed"}), 500

