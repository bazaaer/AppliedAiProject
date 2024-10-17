# backend/api/routes.py

from flask import Blueprint, request, jsonify
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Create a blueprint
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/api', methods=['GET'])
def index():
    return 'Klopta API is running!'

@api_blueprint.route('/api/rewrite', methods=['POST'])
def rewrite_text():
    data = request.get_json()
    user_text = data.get('text', '')

    if not user_text:
        return jsonify({'error': 'No text provided'}), 400

    # Create the prompt for GPT-4
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a journalist tasked with rewriting text in the corporate identity of www.antwerpen.be in DUTCH. Don't add or remove any information!!! Here is the original text: "
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )

        # Extract the rewritten text from the response
        rewritten_text = response.choices[0].message.content

        return jsonify({'rewritten_text': rewritten_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
