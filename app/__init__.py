"""
Application Factory - FIXED CORS Configuration + SendGrid Integration
Owner: Ryan
Description: Initializes the Flask app with proper CORS, SendGrid, JWT, DB, and Swagger setup.
"""

import os

from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sendgrid import SendGridAPIClient

from app.config import Config
from app.extensions import db, init_extensions, jwt, ma, mail, migrate
from app.utils.error_handlers import register_error_handlers
from app.utils.jwt_handlers import register_jwt_error_handlers


def create_app(config_class=Config):
    """Application factory pattern for ReelBrief."""

    # Load Environment Variables
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False

    # Initialize all Flask extensions (DB, JWT, Mail, etc.)
    init_extensions(app)

    # Health Check Route
    @app.route("/")
    def home():
        return jsonify({"message": "ReelBrief API is live!"}), 200

    @app.route("/health")
    def health_check():
        """Health check endpoint for Render"""
        return jsonify({
            "status": "healthy", 
            "service": "ReelBrief API",
            "environment": os.environ.get('FLASK_ENV', 'development')
        }), 200

    # Configure JWT identity loaders
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

    # Database setup with production support
    with app.app_context():
        from app.models.deliverable import Deliverable
        from app.models.feedback import Feedback
        from app.models.freelancer import Freelancer
        from app.models.project import Project
        from app.models.review import Review
        from app.models.user import User

        # Only create tables if they don't exist (Render PostgreSQL)
        db.create_all()

    # Register Blueprints
    from app.resources.activity_resource import activity_bp
    from app.resources.auth_resource import auth_bp
    from app.resources.dashboard_resource import dashboard_bp
    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp
    from app.resources.feedback_resource import feedback_bp
    from app.resources.freelancer_resource import freelancer_bp
    from app.resources.invoice_resource import invoice_bp
    from app.resources.project_resource import project_bp
    from app.resources.review_resource import review_bp
    from app.resources.skills_resource import skills_bp
    from app.resources.user_resource import user_bp
    from app.resources.wallet_resource import wallet_bp
    from app.routes.test_notifications import test_bp
    from app.resources.project_approval_resource import project_approval_bp
    from app.resources.portfolio_resource import portfolio_bp
    from app.resources.notification_resource import notification_bp

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
        (wallet_bp, "/api/wallet"),
        (test_bp, "/api"),
        (project_approval_bp, "/api/projects"),
        (portfolio_bp, "/api/portfolio"),
        (notification_bp, "/api/notifications"),
    ]
    for bp, prefix in blueprints:
        app.register_blueprint(bp, url_prefix=prefix)

        # FIXED: CORS Configuration for Production
    # Production CORS setup
    if os.environ.get('FLASK_ENV') == 'production':
        # In production, allow your Vercel domain and any others you need
        frontend_urls = [
            "https://reel-brief-frontend.vercel.app",
            "http://localhost:5173"  # For local testing
        ]
    else:
        # Development
        frontend_urls = ["http://localhost:5173"]

    print(f"CORS configured for origins: {frontend_urls}")

    # Serve uploads (CVs) - with production path adjustment
    @app.route("/uploads/<filename>")
    def serve_uploaded_file(filename):
        upload_dir = os.path.join(os.getcwd(), "uploads")
        # Create uploads directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        return send_from_directory(upload_dir, filename)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": frontend_urls}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
        max_age=3600,
    )

    # Additional CORS headers (backup for preflight requests)
    @app.after_request
    def after_request(response):
        origin = request.headers.get("Origin")
        if origin in frontend_urls:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
        return response

    # Register Error Handlers and Swagger
    register_jwt_error_handlers(jwt)
    register_error_handlers(app)

    # Swagger Documentation 
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