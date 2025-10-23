import os

import sendgrid
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
mail = Mail()


sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
