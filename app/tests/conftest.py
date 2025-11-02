# app/tests/conftest.py
import os
import sys

import pytest

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app, db


@pytest.fixture(scope="session")
def app():
    """Create and configure test application"""
    app = create_app()

    # Configure for testing
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            "JWT_SECRET_KEY": "test-secret-key",
            "SECRET_KEY": "test-secret-key",
        }
    )

    # Push application context
    with app.app_context():
        # Import all models to ensure they are registered with SQLAlchemy
        try:
            from app.models.deliverable import Deliverable
            from app.models.feedback import Feedback
            from app.models.project import Project
            from app.models.user import User
        except ImportError as e:
            print(f"Import error: {e}")
            # Continue anyway - some models might be missing but we'll try

        # Create all tables
        db.create_all()

        yield app

        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def init_database(app):
    """Initialize database with test data"""
    with app.app_context():
        # Clear any existing data
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

        # Import models here to avoid circular imports
        from app.models.project import Project
        from app.models.user import User

        # Create test user
        user = User(
            email="test@example.com",
            password_hash="hashed_password_123",
            first_name="Test",
            last_name="User",
            role="client",
            is_verified=True,
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        # Create test project (if Project model exists)
        try:
            project = Project(
                title="Test Project", description="Test Description", client_id=user.id
            )
            db.session.add(project)
            db.session.commit()
        except Exception as e:
            print(f"Note: Project creation failed: {e}")
            # Continue without project if model doesn't exist

        yield db

        db.session.remove()
