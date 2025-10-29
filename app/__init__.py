from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.extensions import db, jwt, migrate

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.route("/")
    def home():
        return jsonify({"message": "API is live, but empty!"})

    # ----------------------------
    # Initialize extensions
    # ----------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # mail.init_app(app)
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",  # Local dev
                    "https://reel-brief-frontend.vercel.app/",  # Production
                    # ADD VERCEL PREVIEW URLS if needed
                ]
            }
        },
    )

    # ----------------------------
    # Register Blueprints (APIs)
    # ----------------------------

    # Ryan’s routes
    from app.resources.auth_resource import auth_bp
    from app.resources.user_resource import user_bp

    # Caleb’s routes
    from app.resources.project_resource import project_bp
    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp

    # Monica’s route — Freelancer Vetting System 💪🏽
    from app.resources.freelancer_resource import freelancer_bp

    # Register all
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(project_bp, url_prefix="/api/projects")
    app.register_blueprint(deliverable_bp, url_prefix="/api/deliverables")
    app.register_blueprint(escrow_bp, url_prefix="/api/escrow")
    app.register_blueprint(freelancer_bp, url_prefix="/api/freelancers")

    # ----------------------------
    # Swagger Documentation
    # ----------------------------
    from flasgger import Swagger

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

    Swagger(app, config=swagger_config)

    return app
