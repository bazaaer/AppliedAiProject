# api/llm.py
from quart import Blueprint, request, jsonify, current_app
from api.utils import jwt_or_api_key_required
from llm.llm import read_file_contents, write_sentence
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

@llm_blueprint.route("/api/model/rewrite", methods=["POST"])
async def rewrite():
    """
    Handle requests to rewrite text using the LLM with caching.
    """
    try:
        # Get request data
        request_data = await request.get_json()
        text = request_data.get("text")
        user_prompt = request_data.get("user_prompt") 
        regenerate = request_data.get("regenerate", False)

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Generate a cache key based on text and user_prompt
        cache_key = generate_cache_key(f"{text}_{user_prompt or ''}")

        # Check Redis cache for an existing response
        if not regenerate:
            cached_response = llm_cache_store.get(cache_key)
            if cached_response:
                return jsonify({"msg": "Rewrite successful", "data": json.loads(cached_response)}), 200

        # Call the asynchronous write_sentence function
        response = await write_sentence(
            session=current_app.aiohttp_session,
            host=HOST,
            text=text,
            user_prompt=user_prompt
        )

        # Cache the response
        llm_cache_store.set(cache_key, json.dumps(response), ex=REDIS_CACHE_TTL)

        return jsonify({"msg": "Rewrite successful", "data": response}), 200
    except Exception as e:
        current_app.logger.error(f"Rewrite failed with error: {e}")
        return jsonify({"error": "Rewrite failed"}), 500
    
@llm_blueprint.route("/api/model/pipeline", methods=["POST"])
# @jwt_or_api_key_required(["admin", "user"])
async def pipeline():
    """
    Endpoint to score and rewrite sentences as needed.
    """
    try:
        # Get the request data
        request_data = await request.get_json()
        text_input = request_data.get("text", None)
        user_prompt = request_data.get("user_prompt", None)

        # Validate the input
        if not isinstance(text_input, str):
            return jsonify({"error": "Invalid input: 'text' must be a non-empty string"}), 400

        # Split text into sentences
        sentences = text_input.split(". ")
        if not sentences:
            return jsonify({"error": "No valid sentences found in the input"}), 400

        # Clean the sentences by removing HTML tags
        cleaned_sentences = []
        for sentence in sentences:
            soup = BeautifulSoup(sentence, "html.parser")
            cleaned_sentence = soup.get_text(separator=" ").strip()
            if cleaned_sentence:
                cleaned_sentences.append(cleaned_sentence)

        # Score the sentences using the scoring service
        session = current_app.aiohttp_session
        async with session.post(f"{RAY_SERVE_URL}", json={"text": cleaned_sentences}) as score_response:
            if score_response.status != 200:
                return jsonify({
                    "error": "Error from scoring service",
                    "details": await score_response.text()
                }), score_response.status

            scoring_data = await score_response.json()

        # Process the scores and rewrite sentences with score < 0.8
        rewritten_results = []
        for score_entry in scoring_data["sentence_scores"]:
            original_sentence = score_entry["sentence"]
            score = score_entry["score"]

            if score >= 0.95:
                # Add high-score sentences as-is
                rewritten_results.append({
                    "original_sentence": original_sentence,
                    "rewritten_sentence": original_sentence,
                    "score": score
                })
            else:
                # Rewrite low-score sentences
                cache_key = generate_cache_key(f"{original_sentence}_{user_prompt or ''}")
                cached_response = llm_cache_store.get(cache_key)

                if cached_response:
                    rewritten_sentence = json.loads(cached_response).get("data", original_sentence)
                else:
                    try:
                        # Rewrite the sentence using write_sentence
                        print("LLM call")
                        rewrite_response = await write_sentence(
                            session=session,
                            host=HOST,
                            text=original_sentence,
                            user_prompt=user_prompt
                        )
                        rewritten_sentence = rewrite_response  # No `.get()` since it's a string
                        # Cache the rewritten result
                        llm_cache_store.set(cache_key, json.dumps({"data": rewritten_sentence}), ex=REDIS_CACHE_TTL)
                    except Exception as e:
                        current_app.logger.error(f"Failed to rewrite sentence: {original_sentence}. Error: {str(e)}")
                        rewritten_sentence = original_sentence

                rewritten_results.append({
                    "original_sentence": original_sentence,
                    "rewritten_sentence": rewritten_sentence,
                    "score": score
                })

        # Prepare the final response
        response = {
            "sentence_results": rewritten_results
        }

        return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Pipeline failed with error: {e}")
        return jsonify({"error": "Pipeline processing failed", "details": str(e)}), 500
