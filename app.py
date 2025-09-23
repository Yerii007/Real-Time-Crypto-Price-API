# app.py
from flask import Flask
from flask_jwt_extended import JWTManager
from config import DevConfig
from extensions_file import db, cache
from extensions.logger import configure_logging
from utils.background import start_background_updater
from errors import register_error_handlers
import os

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    config_name = os.getenv("FLASK_CONFIG", "DevConfig")
    app.config.from_object(f"config.{config_name}")

    db.init_app(app)   
    jwt.init_app(app)
    cache.init_app(app) 
    configure_logging(app)
    app.logger.info("App initialized")
    register_error_handlers(app)

    from routes.auth import auth_bp
    from routes.prices import prices_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(prices_bp)

    with app.app_context():
        db.create_all()

    start_background_updater(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
