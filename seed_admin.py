"""
seed_admin.py
Creates a default admin user for ReelBrief.
"""

from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin_email = "admin@reelbrief.com"

    # Check if admin exists
    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        print("⚠️ Admin already exists:", existing.email)
    else:
        admin = User(
            first_name="Admin",
            last_name="User",
            email=admin_email,
            role="admin",
            password_hash=generate_password_hash("Admin123!"),
            is_active=True,
            is_verified=True,
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created successfully:", admin.email)
