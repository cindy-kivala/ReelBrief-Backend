"""
Auth Service
Owner: Ryan
Description: Handles authentication logic including registration, login, password hashing, and JWT management.
"""

"""
Auth Service
Owner: Ryan
Description: Handles authentication logic including registration, login, password hashing, and JWT management.
"""

import secrets
from datetime import datetime, timedelta

from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jti
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models.user import User
from app.services.email_service import send_verification_email


# ---------------------------------------------------------------------
# Password Helpers
# ---------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Generate a secure password hash."""
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if the provided password matches the stored hash."""
    return check_password_hash(hashed_password, plain_password)


# ---------------------------------------------------------------------
# Register & Login
# ---------------------------------------------------------------------
def register_user(data: dict):
    """Register a new user."""
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not all([email, password, role]):
        return {"error": "Missing fields"}, 400

    if User.query.filter_by(email=email).first():
        return {"error": "Email already exists"}, 409

    user = User(email=email, role=role)
    user.password_hash = hash_password(password)
    db.session.add(user)
    db.session.commit()

    # Optional: send verification email
    send_verification_email(email, user.id)

    return {"message": "User registered successfully", "user": user.to_dict()}, 201


def login_user(email: str, password: str):
    """Authenticate and return access tokens."""
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return {"error": "Invalid credentials"}, 401

    claims = {"role": user.role, "email": user.email}
    access_token = create_access_token(
        identity=user.id, additional_claims=claims, expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(identity=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    }, 200


# ---------------------------------------------------------------------
# Refresh / Logout
# ---------------------------------------------------------------------
def refresh_access_token(refresh_token: str):
    """Generate a new access token."""
    try:
        decoded = decode_token(refresh_token)
        user_id = decoded.get("sub")
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        claims = {"role": user.role, "email": user.email}
        new_access = create_access_token(
            identity=user_id, additional_claims=claims, expires_delta=timedelta(minutes=30)
        )
        return {"access_token": new_access}, 200
    except Exception as e:
        return {"error": f"Invalid refresh token: {str(e)}"}, 401


revoked_tokens = set()


def revoke_token(jti: str):
    """Revoke a JWT token (logout)."""
    revoked_tokens.add(jti)
    return {"message": "Token revoked"}, 200


def is_token_revoked(decoded_token):
    """Check if token is revoked."""
    jti = decoded_token["jti"]
    return jti in revoked_tokens


# TODO: Ryan - Implement Auth Service
#
# Required functions:
#
# def register_user(data):
#     """Register a new user."""
#
# def login_user(email, password):
#     """Authenticate and return access tokens."""
#
# def verify_password(plain_password, hashed_password):
#     """Check password validity."""
#
# def refresh_access_token(refresh_token):
#     """Generate a new access token."""
#
# def revoke_token(jti):
#     """Revoke a JWT token (logout)."""
