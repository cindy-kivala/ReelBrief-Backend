import os

import sendgrid
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
