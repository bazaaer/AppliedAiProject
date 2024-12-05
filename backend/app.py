from flask import Flask, jsonify, request
from openai import OpenAI

client = OpenAI()
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing


@app.route("/api", methods=["GET"])
def index():
    return "Klopta API is running!"


@app.route("/api/rewrite", methods=["POST"])
def rewrite_text():
    data = request.get_json()
    user_text = data.get("text", "")

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    # Create the prompt for GPT-4

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a journalist tasked with rewriting text in the corporate identity of www.antwerpen.be in DUTCH. Dont add or remove any information!!! Here is the original text: ",
                },
                {"role": "user", "content": user_text},
            ],
        )

        # Extract the rewritten text from the response
        rewritten_text = response.choices[0].message.content

        return jsonify({"rewritten_text": rewritten_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
