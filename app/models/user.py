"""
User Model - Authentication & RBAC
Owner: Ryan
Description: Handles user authentication, roles (admin/freelancer/client), and profile data.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    # -------------------- Core Fields --------------------
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)

    # -------------------- Authentication & RBAC --------------------
    role = db.Column(db.String(50), nullable=False)  # admin, freelancer, client
    is_active = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), unique=True)
    reset_token = db.Column(db.String(255))
    reset_token_expires = db.Column(db.DateTime)

    # -------------------- Timestamps --------------------
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # -------------------- Relationships --------------------
    freelancer_profile = db.relationship(
        "FreelancerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    # -------------------- Methods --------------------
    def set_password(self, password: str):
        """Hash and store password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Validate password hash."""
        return check_password_hash(self.password_hash, password)

    def get_identity(self):
        """Return identity payload for JWT claims."""
        return {"id": self.id, "email": self.email, "role": self.role}

    def to_dict(self):
        """Return a JSON-serializable user representation."""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
