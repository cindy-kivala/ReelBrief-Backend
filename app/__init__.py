from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, jwt, mail

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['FRONTEND_URL']}})
    
    # Register blueprints
    from app.resources.auth_resource import auth_bp
    from app.resources.user_resource import user_bp
    from app.resources.project_resource import project_bp
    from app.resources.deliverable_resource import deliverable_bp
    from app.resources.escrow_resource import escrow_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(project_bp, url_prefix='/api/projects')
    app.register_blueprint(deliverable_bp, url_prefix='/api/deliverables')
    app.register_blueprint(escrow_bp, url_prefix='/api/escrow')
    
    # Swagger documentation
    from flasgger import Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/"
    }
    Swagger(app, config=swagger_config)
    
    return app
