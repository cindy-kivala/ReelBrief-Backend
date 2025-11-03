# seed_admin.py
"""
Seed (or update) an admin user for ReelBrief.

Usage:
  (venv) python seed_admin.py
  (venv) python seed_admin.py --email you@example.com --password Secret123! --first Admin --last User
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect

# -------------------------------------------------------------------
# Load .env from backend root BEFORE importing/creating the app
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent       # backend root
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(ENV_PATH)  # ensures DATABASE_URL is available

# -------------------------------------------------------------------
# App imports (after env is loaded)
# -------------------------------------------------------------------
from app import create_app                      # noqa: E402
from app.extensions import db                   # noqa: E402
try:
    from app.models.user import User            # noqa: E402
except Exception:
    from app.models import User                 # noqa: E402


def ensure_users_table(app) -> None:
    """Print DB URI and ensure 'users' table exists, else instruct migrations."""
    with app.app_context():
        uri = app.config.get("SQLALCHEMY_DATABASE_URI")
        print(f"🔌 DB in use → {uri}")
        insp = inspect(db.engine)
        if not insp.has_table("users"):
            print(
                "\n❗ The 'users' table does not exist in this database.\n"
                "   Run your migrations first, then re-run this script:\n"
                "     (venv) export FLASK_APP=app:create_app  # fish: set -x FLASK_APP app:create_app\n"
                "     (venv) flask db upgrade\n"
            )
            sys.exit(1)


def upsert_admin(app, email: str, password: str, first: str, last: str) -> None:
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"🔁 Admin already exists → {email}. Updating details…")
            user.first_name = first
            user.last_name = last
            user.role = "admin"
            user.is_active = True
            user.is_verified = True
            user.password_hash = generate_password_hash(password)
            user.last_login = user.last_login or datetime.utcnow()
        else:
            print(f"➕ Creating admin → {email}")
            user = User(
                email=email,
                first_name=first,
                last_name=last,
                role="admin",
                is_active=True,
                is_verified=True,
                password_hash=generate_password_hash(password),
                last_login=datetime.utcnow(),
            )
            db.session.add(user)

        db.session.commit()
        print("\n✅ Admin ready.")
        print(f"   Email:    {email}")
        print(f"   Password: {password}   (change in production!)")
        print(f"   Role:     {user.role}\n")


def main():
    parser = argparse.ArgumentParser(description="Seed (or update) an admin user.")
    parser.add_argument("--email", default="admin@reelbrief.com")
    parser.add_argument("--password", default="Admin123!")
    parser.add_argument("--first", default="Ruri")
    parser.add_argument("--last", default="Admin")
    args = parser.parse_args()

    app = create_app()
    ensure_users_table(app)
    upsert_admin(app, args.email, args.password, args.first, args.last)


if __name__ == "__main__":
    main()
