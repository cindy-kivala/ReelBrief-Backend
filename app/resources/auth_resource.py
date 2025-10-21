"""
Authentication Resource - Auth Endpoints
Owner: Ryan
Description: Handles user registration, login, refresh token, email verification, and password reset.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

from app import db
from app.models import User
from app.services.email_service import send_verification_email, send_password_reset_email

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


# --------------------------------------------------------
# POST /api/auth/register
# --------------------------------------------------------
@auth_bp.post("/register")
def register():
    data = request.get_json()
    required_fields = ["email", "password", "role", "first_name", "last_name"]

    if not all(data.get(field) for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    # Hash password
    hashed_password = generate_password_hash(data["password"])

    # Create verification token
    verification_token = secrets.token_urlsafe(32)

    user = User(
        email=data["email"],
        password_hash=hashed_password,
        role=data["role"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        is_active=False,
        is_verified=False,
        verification_token=verification_token,
    )

    db.session.add(user)
    db.session.commit()

    # Send verification email
    send_verification_email(user.email, verification_token)

    return jsonify({"message": "User registered. Please verify your email."}), 201


# --------------------------------------------------------
# POST /api/auth/login
# --------------------------------------------------------
@auth_bp.post("/login")
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 403

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # JWT claims
    claims = {"role": user.role, "email": user.email}
    access_token = create_access_token(
        identity=user.id,
        additional_claims=claims,
        expires_delta=timedelta(hours=3)
    )
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


# --------------------------------------------------------
# POST /api/auth/refresh
# --------------------------------------------------------
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Issue new access token using refresh token"""
    current_user = get_jwt_identity()
    new_access_token = create_access_token(
        identity=current_user, expires_delta=timedelta(hours=3)
    )
    return jsonify({"access_token": new_access_token}), 200


# --------------------------------------------------------
# POST /api/auth/verify-email
# --------------------------------------------------------
@auth_bp.post("/verify-email")
def verify_email():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "Missing verification token"}), 400

    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 404

    user.is_verified = True
    user.is_active = True
    user.verification_token = None
    db.session.commit()

    return jsonify({"message": "Email verified successfully"}), 200


# --------------------------------------------------------
# GET /api/auth/me
# --------------------------------------------------------
@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the currently authenticated user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


# --------------------------------------------------------
# POST /api/auth/reset-password
# --------------------------------------------------------
@auth_bp.post("/reset-password")
def reset_password():
    """
    Step 1: User submits email -> sends reset link
    Step 2: User submits token + new_password -> updates password
    """
    data = request.get_json()
    email = data.get("email")
    token = data.get("token")
    new_password = data.get("new_password")

    # Step 1: Request password reset link
    if email and not token:
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Email not found"}), 404

        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        send_password_reset_email(user.email, reset_token)
        return jsonify({"message": "Password reset link sent to your email"}), 200

    # Step 2: Use token to reset password
    if token and new_password:
        user = User.query.filter_by(reset_token=token).first()
        if not user or user.reset_token_expires < datetime.utcnow():
            return jsonify({"error": "Invalid or expired reset token"}), 400

        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()

        return jsonify({"message": "Password reset successful"}), 200

    return jsonify({"error": "Invalid request"}), 400
