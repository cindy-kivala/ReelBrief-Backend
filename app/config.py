import os
from datetime import timedelta

class Config:
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "devsecretkey")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///reelbrief.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=3)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # SendGrid / Email
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "example@example.com")
    SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "ReelBrief Notifications")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5174")  # Frontend for verify links

    # CORS (frontends allowed)
    FRONTEND_URLS = os.getenv(
        "FRONTEND_URLS",
        "http://localhost:5173,http://localhost:5174,https://reelbrief-frontend.vercel.app"
    )
