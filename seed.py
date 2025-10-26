"""
seed.py
Owner: Ryan
Description: Seeds the PostgreSQL database with initial test users (Admin, Freelancer, Client).
Usage:
    python seed.py
"""

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash


def seed_users():
    """Populate the database with test users."""
    print("🚀 Seeding database...")

    # Optional: Clear existing users (for development use only)
    db.session.query(User).delete()

    # -------------------- Create Users --------------------
    users = [
        User(
            first_name="Admin",
            last_name="User",
            email="admin@reelbrief.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            is_active=True,
            is_verified=True
        ),
        User(
            first_name="Freelancer",
            last_name="One",
            email="freelancer@reelbrief.com",
            password_hash=generate_password_hash("freelancer123"),
            role="freelancer",
            is_active=True,
            is_verified=True
        ),
        User(
            first_name="Client",
            last_name="One",
            email="client@reelbrief.com",
            password_hash=generate_password_hash("client123"),
            role="client",
            is_active=True,
            is_verified=True
        ),
    ]

    # -------------------- Commit to DB --------------------
    db.session.add_all(users)
    db.session.commit()

    print("✅ Database seeded successfully with Admin, Freelancer, and Client users!")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_users()
