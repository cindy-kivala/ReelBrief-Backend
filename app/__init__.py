"""
Application Factory - FIXED CORS Configuration + SendGrid Integration
Owner: Ryan
Description: Initializes the Flask app with proper CORS, SendGrid, JWT, DB, and Swagger setup.
"""

import os
from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from sendgrid import SendGridAPIClient

from app.config import Config
from app.extensions import init_extensions, db, migrate, jwt, ma, mail
from app.utils.error_handlers import register_error_handlers
from app.utils.jwt_handlers import register_jwt_error_handlers


def create_app(config_class=Config):
    """Application factory pattern for ReelBrief."""

    # Load Environment Variables
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False

    # ✅ Initialize all Flask extensions (DB, JWT, Mail, etc.)
    init_extensions(app)

    # ✅ Initialize SendGrid client globally
   
    # Health Check Route
    @app.route("/")
    def home():
        return jsonify({"message": "ReelBrief API is live!"}), 200

    # ✅ Configure JWT identity loaders
    from app.models.user import User

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """Defines what to store in the JWT token (usually the user ID)."""
        if isinstance(user, User):
            return user.id
        elif isinstance(user, dict):
            return user.get("id")
        return user

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Loads a user from JWT token."""
        identity = jwt_data["sub"]
        return User.query.get(identity)

    # ✅ Ensure all models are imported and relationships configured
    with app.app_context():
        from app.models.user import User
        from app.models.project import Project
        from app.models.deliverable import Deliverable
        from app.models.feedback import Feedback
        from app.models.freelancer import Freelancer
        from app.models.review import Review

        db.create_all()

    # ✅ Register Blueprints
    from app.resources.auth_resource import auth_bp
    from app.resources.dashboard_resource import dashboard_bp
    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp
    from app.resources.feedback_resource import feedback_bp
    from app.resources.invoice_resource import invoice_bp
    from app.resources.review_resource import review_bp
    from app.resources.user_resource import user_bp
    from app.resources.skills_resource import skills_bp
    from app.resources.project_resource import project_bp
    from app.resources.activity_resource import activity_bp
    from app.resources.freelancer_resource import freelancer_bp
    from app.routes.test_notifications import test_bp

    blueprints = [
        (auth_bp, "/api/auth"),
        (user_bp, "/api/users"),
        (project_bp, "/api/projects"),
        (deliverable_bp, "/api/deliverable"),
        (feedback_bp, "/api/feedback"),
        (escrow_bp, "/api/escrow"),
        (freelancer_bp, "/api/freelancers"),
        (invoice_bp, "/api/invoices"),
        (dashboard_bp, "/api/dashboard"),
        (review_bp, "/api/reviews"),
        (activity_bp, "/api/activity"),
        (skills_bp, "/api"),
        (test_bp, "/api"),
    ]
    for bp, prefix in blueprints:
        app.register_blueprint(bp, url_prefix=prefix)

    # ✅ FIXED: CORS Configuration
    frontend_urls_str = os.getenv(
        "FRONTEND_URLS",
        "http://localhost:5173,https://reel-brief-frontend.vercel.app",
    )
    frontend_urls = [url.strip() for url in frontend_urls_str.split(",")]
    print(f"✅ CORS configured for origins: {frontend_urls}")

    CORS(
        app,
        resources={r"/api/*": {"origins": frontend_urls}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
        max_age=3600,
    )

    # ✅ Additional CORS headers (backup for preflight requests)
    @app.after_request
    def after_request(response):
        origin = request.headers.get("Origin")
        if origin in frontend_urls:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
        return response

    # ✅ Register Error Handlers and Swagger
    register_jwt_error_handlers(jwt)
    register_error_handlers(app)

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda r: True,
                "model_filter": lambda t: True,
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
            "contact": {"name": "ReelBrief Dev Team", "email": "support@reelbrief.com"},
        },
        "basePath": "/",
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    return app
