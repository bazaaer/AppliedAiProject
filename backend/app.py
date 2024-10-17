from gevent import monkey
monkey.patch_all()  # Apply Gevent monkey-patching

from flask import Flask
from flask_cors import CORS
from api import api_blueprint, auth_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Use a secure key here
CORS(app)  # Enable Cross-Origin Resource Sharing

# Register the blueprints
app.register_blueprint(api_blueprint)
app.register_blueprint(auth_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
