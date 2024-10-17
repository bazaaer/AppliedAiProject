# backend/app.py

from gevent import monkey
monkey.patch_all()  # Apply Gevent monkey-patching

from flask import Flask
from flask_cors import CORS
from api import api_blueprint

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Register the blueprint
app.register_blueprint(api_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
