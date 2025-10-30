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
from app.extensions import init_extensions, db, migrate, jwt, ma, mail
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

    # CRITICAL FIX: Import models to configure relationships
    with app.app_context():
        from app.models.user import User
        from app.models.project import Project
        from app.models.deliverable import Deliverable
        from app.models.feedback import Feedback
        from app.models.freelancer import Freelancer
        
        # This forces SQLAlchemy to configure all relationships
        db.create_all()

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
    from app.resources.dashboard_resource import dashboard_bp

    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp
    from app.resources.feedback_resource import feedback_bp
    from app.resources.invoice_resource import invoice_bp
    from app.resources.review_resource import review_bp
    from app.resources.user_resource import user_bp
    # Serve uploads (CVs)
    # @app.route("/uploads/<filename>")
    # def serve_uploaded_file(filename):
    #     upload_dir = os.path.join(os.getcwd(), "uploads")
    #     return send_from_directory(upload_dir, filename)

    # # Extensions (incl. SendGrid)
    # init_extensions(app)

    # # CORS
    # frontend_urls = app.config.get("FRONTEND_URLS", "").split(",")
    # app.logger.info(f"Allowed CORS Origins: {frontend_urls}")
    # CORS(
    #     app,
    #     resources={r"/api/*": {"origins": frontend_urls}},
    #     supports_credentials=True,
    #     allow_headers=["Content-Type", "Authorization"],
    #     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    # )

    # # Error handlers
    # from app.extensions import jwt
    # register_jwt_error_handlers(jwt)
    # register_error_handlers(app)

    # # Blueprints
    # from app.resources.auth_resource import auth_bp
    # from app.resources.user_resource import user_bp
    # from app.resources.deliverable_resource import deliverable_bp
    # from app.resources.escrow_resource import escrow_bp
    # from app.resources.feedback_resource import feedback_bp
    # # from app.resources.project_resource import project_bp

    # Caleb's routes
    from app.resources.project_resource import project_bp
    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp
    from app.resources.activity_resource import activity_bp

    # Monica's route — Freelancer Vetting System 
    from app.resources.freelancer_resource import freelancer_bp

    # Register all
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
    # -------------------- Swagger Documentation --------------------
    swagger_config = {
        "headers": [],
        "specs": [{"endpoint": "apispec", "route": "/apispec.json", "rule_filter": lambda r: True, "model_filter": lambda t: True}],
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

    # Initialize Swagger ONCE with both config and template
    Swagger(app, config=swagger_config, template=swagger_template)

    #  Return Configured App 
    # with app.app_context():
    #     print("\n=== Registered Routes ===")
    #     for rule in app.url_map.iter_rules():
    #         print(f"{rule.endpoint}: {rule.rule} {list(rule.methods - {'OPTIONS', 'HEAD'})}")
    #     print("========================\n")

    
    # return app
    # Swagger(app, config=swagger_config, template=swagger_template)

    # # Ensure uploads dir exists
    # os.makedirs(os.path.join(os.getcwd(), "uploads"), exist_ok=True)

    # # Log DB (sanitized)
    # db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    # app.logger.info(f"🔌 DB in use → {db_uri.split('@')[-1] if '@' in db_uri else db_uri}")

    return app
