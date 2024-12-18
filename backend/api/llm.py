# api/llm.py
from quart import Blueprint, request, jsonify, current_app
from api.utils import jwt_or_api_key_required
from llm.llm import read_file_contents, process_text_before_rewriting, process_text_after_rewriting
from config import llm_cache_store, REDIS_CACHE_TTL
import json
import hashlib
import os
from ollama import AsyncClient
from bs4 import BeautifulSoup
import asyncio

llm_blueprint = Blueprint('llm', __name__)

RAY_SERVE_URL = os.getenv("RAY_SERVE_URL", "http://localhost:8000")
SCHRIJFASSISTENT_MODELFILE = "llm/Modelfile_schrijfassistent"
STIJLASSISTENT_MODELFILE = "llm/Modelfile_stijlassistent"
HOST = os.getenv("OLLAMA_URL", "http://ollama:11434")
CLIENT = AsyncClient(host=HOST)

async def initialize_models():
    """
    Preload models on Ollama using the shared AsyncClient.
    """
    try:
        client = AsyncClient(host=HOST)

        await client.create(
            model="schrijfassistent",
            modelfile=read_file_contents(SCHRIJFASSISTENT_MODELFILE))

        await client.create(
            model="stijlassistent",
            modelfile=read_file_contents(STIJLASSISTENT_MODELFILE)
        )

        current_app.logger.info("Models 'schrijfassistent' and 'stijlassistent' initialized successfully.")
    except Exception as e:
        current_app.logger.error(f"Model initialization failed: {e}")

def generate_cache_key(sentence: str) -> str:
    """
    Generate a unique cache key for a given sentence.
    """
    return hashlib.sha256(sentence.encode()).hexdigest()

async def fetch_response_stream(client, model, prompt):
    """Helper function to stream the response from the Ollama API."""
    try:
        async for part in await client.generate(
            model=model, prompt=prompt, stream=True
        ):
            yield part["response"]
    except Exception as e:
        raise ValueError(f"Error generating response from model '{model}': {e}")

async def fetch_response_non_stream(client, model, prompt):
    """Helper function to fetch the full response from the Ollama API."""
    try:
        response = await client.generate(model=model, prompt=prompt, stream=False)
        return response["response"]
    except Exception as e:
        raise ValueError(f"Error generating response from model '{model}': {e}")

@llm_blueprint.route("/api/model/rewrite", methods=["POST"])
@jwt_or_api_key_required(["admin", "user"])
async def rewrite():
    """
    Handle requests to rewrite text using the LLM with optional streaming.
    """
    try:
        # Get request data
        request_data = await request.get_json()
        text = request_data.get("text")
        user_prompt = request_data.get("user_prompt")
        regenerate = request_data.get("regenerate", "false").lower() == "true"
        stream = request_data.get("stream", "false").lower() == "true"

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Generate a cache key based on text and user_prompt
        cache_key = generate_cache_key(f"{text}_{user_prompt or ''}")

        if not regenerate and not stream:
            cached_response = llm_cache_store.get(cache_key)
            if cached_response:
                return jsonify({"msg": "Rewrite successful", "data": json.loads(cached_response)}), 200

        text = process_text_before_rewriting(text)
        if user_prompt:
            first_model_prompt = f"{user_prompt}:\n\n{text}"
        else:
            first_model_prompt =f"Pas de schrijf regels toe op deze zin:\n\n{text}"

        # Fetch the response from the first model (non-streaming)
        rewritten_response = await fetch_response_non_stream(CLIENT, "schrijfassistent", first_model_prompt)

        # Use the output from the first model as input for the second model
        second_model_prompt = f"Pas de stijlregels toe op deze zin: {rewritten_response}"

        # Fetch the response from the second model (conditionally streaming)
        if stream:
            async def stream_response():
                async for chunk in fetch_response_stream(CLIENT, "stijlassistent", second_model_prompt):
                    yield chunk

            return current_app.response_class(stream_response(), content_type="text/plain", status=200)
        else:
            styled_response = await fetch_response_non_stream(CLIENT, "stijlassistent", second_model_prompt)

            styled_response = process_text_after_rewriting(styled_response)

            # Cache the response
            llm_cache_store.set(cache_key, json.dumps(styled_response), ex=REDIS_CACHE_TTL)
            return jsonify({"msg": "Rewrite successful", "data": styled_response}), 200

    except Exception as e:
        current_app.logger.error(f"Rewrite failed with error: {e}")
        return jsonify({"error": "Rewrite failed"}), 500


@llm_blueprint.route("/api/model/pipeline", methods=["POST"])
@jwt_or_api_key_required(["admin", "user"])
async def pipeline():
    """
    Combined pipeline to score sentences and rewrite those with low scores.
    """
    try:
        # Get request data
        request_data = await request.get_json()
        text = request_data.get("text")
        regenerate = request_data.get("regenerate", "false").lower() == "true"

        if not text or not isinstance(text, str):
            return jsonify({"error": "Invalid input: 'text' must be a non-empty string"}), 400

        # Clean the text by removing HTML tags
        soup = BeautifulSoup(text.strip(), "html.parser")
        cleaned_text = soup.get_text(separator=" ").strip()

        if not cleaned_text:
            return jsonify({"error": "Input becomes empty after removing HTML tags"}), 400

        session = current_app.aiohttp_session

        # Step 1: Score sentences using Ray Serve
        async with session.post(f"{RAY_SERVE_URL}", json={"text": [cleaned_text]}) as response:
            if response.status != 200:
                return jsonify({
                    "error": "Error from Ray Serve",
                    "details": await response.text()
                }), response.status

            ray_response = await response.json()
            sentence_scores = ray_response.get("sentence_scores", [])

        if not sentence_scores:
            return jsonify({"error": "No sentence scores returned from Ray Serve"}), 500

        # Step 2: Rewrite low-score sentences
        low_score_sentences = [s for s in sentence_scores if s["score"] < 0.8]
        cached_responses = {}
        non_cached_sentences = []

        for sentence_data in low_score_sentences:
            sentence = sentence_data["sentence"]
            cache_key = generate_cache_key(sentence)
            cached_response = llm_cache_store.get(cache_key) if not regenerate else None
            if cached_response:
                cached_responses[sentence] = json.loads(cached_response)
            else:
                non_cached_sentences.append(sentence)

        try:
            if non_cached_sentences:
                first_model_prompts = [f"Pas de schrijf regels toe op deze zin:\n\n{process_text_before_rewriting(sentence)}" for sentence in non_cached_sentences]
                rewritten_responses = await asyncio.gather(
                    *[fetch_response_non_stream(CLIENT, "schrijfassistent", prompt) for prompt in first_model_prompts]
                )

                second_model_prompts = [f"Pas de stijlregels toe op deze zin: {response}" for response in rewritten_responses]
                styled_responses = await asyncio.gather(
                    *[fetch_response_non_stream(CLIENT, "stijlassistent", prompt) for prompt in second_model_prompts]
                )

                for sentence, styled_response in zip(non_cached_sentences, styled_responses):
                    styled_response = process_text_after_rewriting(styled_response)
                    cache_key = generate_cache_key(sentence)
                    llm_cache_store.set(cache_key, json.dumps(styled_response), ex=REDIS_CACHE_TTL)
                    cached_responses[sentence] = styled_response

        except Exception as e:
            current_app.logger.error(f"Error rewriting sentences: {e}")

        results = [
            {
                "original_sentence": sentence_data["sentence"],
                "rewritten_sentence": cached_responses.get(sentence_data["sentence"], sentence_data["sentence"]),
                "score": sentence_data["score"]
            }
            for sentence_data in sentence_scores
        ]

        return jsonify({"results": results}), 200

    except Exception as e:
        current_app.logger.error(f"Full pipeline failed with error: {e}")
        return jsonify({"error": "Full pipeline failed", "details": str(e)}), 500