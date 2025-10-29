"""
Application Factory
Owner: Ryan
Description: Initializes the Flask app, extensions, blueprints, and error handlers.
"""

import os
from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from app.config import Config
from app.extensions import init_extensions
from app.utils.error_handlers import register_error_handlers
from app.utils.jwt_handlers import register_jwt_error_handlers


def create_app(config_class=Config):
    """Application factory pattern for ReelBrief."""
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Health
    @app.route("/")
    def home():
        return jsonify({"message": "🎬 ReelBrief API is live!"}), 200

    # Serve uploads (CVs)
    @app.route("/uploads/<filename>")
    def serve_uploaded_file(filename):
        upload_dir = os.path.join(os.getcwd(), "uploads")
        return send_from_directory(upload_dir, filename)

    # Extensions (incl. SendGrid)
    init_extensions(app)

    # CORS
    frontend_urls = app.config.get("FRONTEND_URLS", "").split(",")
    app.logger.info(f"✅ Allowed CORS Origins: {frontend_urls}")
    CORS(
        app,
        resources={r"/api/*": {"origins": frontend_urls}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Error handlers
    from app.extensions import jwt
    register_jwt_error_handlers(jwt)
    register_error_handlers(app)

    # Blueprints
    from app.resources.auth_resource import auth_bp
    from app.resources.user_resource import user_bp
    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp
    from app.resources.feedback_resource import feedback_bp
    # from app.resources.project_resource import project_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(deliverable_bp, url_prefix="/api/deliverables")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(escrow_bp, url_prefix="/api/escrow")
    # app.register_blueprint(project_bp, url_prefix="/api/projects")

    # Swagger
    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": "apispec", "route": "/apispec.json", "rule_filter": lambda r: True, "model_filter": lambda t: True}],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/",
    }
    swagger_template = {
        "info": {
            "title": "🎬 ReelBrief API",
            "version": "1.0",
            "description": "Backend API for the ReelBrief Creative Management Platform.",
            "contact": {"name": "ReelBrief Dev Team", "email": "support@reelbrief.com"},
        },
        "basePath": "/",
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    # Ensure uploads dir exists
    os.makedirs(os.path.join(os.getcwd(), "uploads"), exist_ok=True)

    # Log DB (sanitized)
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    app.logger.info(f"🔌 DB in use → {db_uri.split('@')[-1] if '@' in db_uri else db_uri}")

    return app
