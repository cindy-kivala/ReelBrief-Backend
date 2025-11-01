import os
import sendgrid
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
mail = Mail()

# Initialized after env is loaded
sg = None

def init_extensions(app):
    """Initialize Flask extensions and SendGrid client AFTER env is loaded."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    mail.init_app(app)

    global sg
    api_key = app.config.get("SENDGRID_API_KEY") or os.getenv("SENDGRID_API_KEY")
    if api_key:
        try:
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            app.logger.info("✅ SendGrid client initialized")
        except Exception as e:
            sg = None
            app.logger.error(f"❌ SendGrid init failed: {e}")
    else:
        app.logger.warning("⚠️ SENDGRID_API_KEY not set; email sending disabled")
