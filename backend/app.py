# app.py
from quart import Quart
from quart_cors import cors
from quart_jwt_extended import JWTManager
import os
from config import ACCESS_EXPIRES, revoked_store
from dotenv import load_dotenv

load_dotenv()

app = Quart(__name__)
app = cors(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'my_precious')
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

jwt = JWTManager(app)

from api import auth_blueprint, api_blueprint
app.register_blueprint(auth_blueprint)
app.register_blueprint(api_blueprint)

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    return revoked_store.get(jti) is not None

@app.before_serving
async def startup():
    from api.auth import insert_admin_user
    await insert_admin_user()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
