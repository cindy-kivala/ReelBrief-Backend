"""
Application Factory - FIXED CORS Configuration
Owner: Ryan
Description: Initializes the Flask app with proper CORS setup.
"""

import os
from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
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

    # Health Check Route 
    @app.route("/")
    def home():
        return jsonify({"message": "ReelBrief API is live!"}), 200

    # Initialize Extensions 
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    mail.init_app(app)

    # CRITICAL: Configure JWT user identity and lookup
    from app.models.user import User
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """
        This function receives whatever is passed as 'identity' in create_access_token()
        It should return a simple, serializable identity (usually user ID)
        """
        # Handle both User objects and integer IDs
        if isinstance(user, User):
            return user.id  # Return just the ID for the token
        elif isinstance(user, dict):
            return user.get('id')  # Extract ID from dict
        else:
            return user  # Assume it's already an ID

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        This function receives the identity from the token and loads the full User object
        """
        identity = jwt_data["sub"]  # This will be the user ID (integer)
        
        # The identity should be the user ID from user_identity_lookup
        return User.query.get(identity)

    # CRITICAL FIX: Import models to configure relationships
    with app.app_context():
        from app.models.user import User
        from app.models.project import Project
        from app.models.deliverable import Deliverable
        from app.models.feedback import Feedback
        from app.models.freelancer import Freelancer
        from app.models.review import Review
        
        # This forces SQLAlchemy to configure all relationships
        db.create_all()

    # Register Blueprints BEFORE CORS
    from app.resources.auth_resource import auth_bp
    from app.resources.dashboard_resource import dashboard_bp
    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp
    from app.resources.feedback_resource import feedback_bp
    from app.resources.invoice_resource import invoice_bp
    from app.resources.review_resource import review_bp
    from app.resources.user_resource import user_bp
    from app.resources.skills_resource import skills_bp
    from app.routes.test_notifications import test_bp

    # Caleb's routes
    from app.resources.project_resource import project_bp
    from app.resources.activity_resource import activity_bp
    
    # Monica's route — Freelancer Vetting System 
    from app.resources.freelancer_resource import freelancer_bp

    # Register all blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(project_bp, url_prefix="/api/projects")
    app.register_blueprint(deliverable_bp, url_prefix="/api/deliverable")
    app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
    app.register_blueprint(escrow_bp, url_prefix="/api/escrow")
    app.register_blueprint(freelancer_bp, url_prefix="/api/freelancers")
    app.register_blueprint(invoice_bp, url_prefix="/api/invoices")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(review_bp, url_prefix="/api/reviews")
    app.register_blueprint(activity_bp, url_prefix="/api/activity")
    app.register_blueprint(skills_bp, url_prefix="/api")
    app.register_blueprint(test_bp, url_prefix="/api")

    # FIXED: CORS Configuration AFTER Blueprint Registration
    # Load from .env → FRONTEND_URLS=http://localhost:5173,https://reel-brief-frontend.vercel.app
    frontend_urls_str = os.getenv("FRONTEND_URLS", "http://localhost:5173")
    frontend_urls = [url.strip() for url in frontend_urls_str.split(",")]
    
    # Log configured origins for debugging
    print(f"CORS configured for origins: {frontend_urls}")

    # Simplified and more permissive CORS configuration
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": frontend_urls,
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "expose_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "max_age": 3600
            }
        },
        supports_credentials=True
    )

    # Add CORS headers to all responses (backup method)
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in frontend_urls:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
        return response

    # Register Error Handlers (AFTER CORS)
    register_jwt_error_handlers(jwt)
    register_error_handlers(app)

    # Swagger Documentation
    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": "apispec", "route": "/apispec.json", "rule_filter": lambda r: True, "model_filter": lambda t: True}],
        "static_url_path": "/flaggger_static",
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

    # Initialize Swagger
    Swagger(app, config=swagger_config, template=swagger_template)

    return app