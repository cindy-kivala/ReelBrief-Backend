"""
User Model - Authentication & RBAC
Owner: Ryan (merged)
Description: Core user entity with auth flags, JWT helpers, and profile/notification relationships.
"""

from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    # Core Fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)

    # Authentication & RBAC 
    role = db.Column(db.String(50), nullable=False, default="freelancer")
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), unique=True)
    reset_token = db.Column(db.String(255))
    reset_token_expires = db.Column(db.DateTime)

    # Timestamps 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    freelancer_profile = db.relationship(
        "FreelancerProfile",
        back_populates="user",
        uselist=False,
        foreign_keys="FreelancerProfile.user_id",
    )

    portfolio_items = db.relationship("PortfolioItem", back_populates="freelancer", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_identity(self) -> dict:
        return {"id": self.id, "email": self.email, "role": self.role}

    def to_dict(self) -> dict:
        user_dict = {
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
        
        # Include freelancer profile data if it exists
        if self.role == "freelancer" and self.freelancer_profile:
            user_dict["freelancer_profile"] = self.freelancer_profile.to_dict()
            
        return user_dict

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"