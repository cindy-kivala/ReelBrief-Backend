"""
Application Factory
Owner: Ryan
Description: Initializes the Flask app, extensions, blueprints, and error handlers.
"""

import os

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.extensions import db, jwt, ma, mail, migrate
from app.utils.error_handlers import register_error_handlers
from app.utils.jwt_handlers import register_jwt_error_handlers


def create_app(config_class=Config):
    """Application factory pattern for ReelBrief."""

    #  Load Environment Variables
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)

    app.url_map.strict_slashes = False

    #  Health Check Route 
    @app.route("/")
    def home():
        return jsonify({"message": "ReelBrief API is live!"}), 200

    #  Initialize Extensions 
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    mail.init_app(app)

     # Load from .env → FRONTEND_URLS=http://localhost:5173,https://reelbrief.vercel.app
    frontend_urls = os.getenv("FRONTEND_URLS", "http://localhost:5173").split(",")

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": frontend_urls,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "max_age": 3600
            }
        },
        supports_credentials=True
    )

    #  Register Error Handlers 
    register_jwt_error_handlers(jwt)
    register_error_handlers(app)

    #  Register Blueprints 
    from app.resources.auth_resource import auth_bp

    # from app.resources.project_resource import project_bp
    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp
    from app.resources.feedback_resource import feedback_bp
    from app.resources.user_resource import user_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    # app.register_blueprint(project_bp, url_prefix="/api/projects")
    app.register_blueprint(deliverable_bp, url_prefix="/api/deliverable")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(escrow_bp, url_prefix="/api/escrow")

    #  Swagger Documentation 
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/",
    }

    swagger_template = {
        "info": {
            "title": "ReelBrief API",
            "version": "1.0",
            "description": "Backend API for the ReelBrief Creative Management Platform.",
            "contact": {
                "name": "ReelBrief Dev Team",
                "email": "support@reelbrief.com",
            },
        },
        "basePath": "/",
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    #  Return Configured App 
    with app.app_context():
        print("\n=== Registered Routes ===")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule} {list(rule.methods - {'OPTIONS', 'HEAD'})}")
        print("========================\n")

    
    return app
