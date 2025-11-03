import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    # General Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Database - FIXED for Render PostgreSQL with SSL
    if os.environ.get('DATABASE_URL'):
        # Render PostgreSQL (production) - fix connection string with SSL
        database_url = os.environ.get('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://')
        # Add SSL requirement for Render
        if 'render.com' in database_url and 'sslmode' not in database_url:
            database_url += '?sslmode=require'
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Local development
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "DATABASE_URL", 
            "postgresql://reelbrief_user:cindy123@localhost:5432/reelbrief_db"
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # SendGrid
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "michenicaleb@gmail.com")
    SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "ReelBrief Notifications")

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    # CORS / Frontend
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    FRONTEND_URLS = os.getenv("FRONTEND_URLS", "http://localhost:5173")

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    STRICT_SLASHES = False