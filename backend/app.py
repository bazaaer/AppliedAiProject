from quart import Quart, redirect, send_from_directory
from quart_cors import cors
from quart_jwt_extended import JWTManager
import os
from config import ACCESS_EXPIRES, revoked_store
from api import auth_blueprint, model_blueprint, users_bleuprint, api_keys_blueprint, llm_blueprint
from config import ADMIN_USERNAME, ADMIN_PASSWORD
import aiohttp


app = Quart(__name__, static_folder="static")
app = cors(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'my_precious')
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

jwt = JWTManager(app)

app.register_blueprint(auth_blueprint)
app.register_blueprint(model_blueprint)
app.register_blueprint(users_bleuprint)
app.register_blueprint(api_keys_blueprint)
app.register_blueprint(llm_blueprint)

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    return revoked_store.get(jti) is not None

@app.route('/api/docs')
async def swagger_ui():
    return redirect('/api/docs/index.html')
    
@app.route('/api/docs/<path:filename>')
async def swagger_ui_files(filename):
    return await send_from_directory(app.static_folder + '/swagger-ui', filename)

@app.before_serving
async def startup():
    from api.users import insert_admin_user
    await insert_admin_user(ADMIN_USERNAME, ADMIN_PASSWORD)
    from db import create_indexes
    await create_indexes()

@app.before_serving
async def create_session():
    app.aiohttp_session = aiohttp.ClientSession()

@app.after_serving
async def close_session():
    await app.aiohttp_session.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
    