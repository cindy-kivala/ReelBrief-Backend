"""
Authentication Resource - Auth Endpoints
Owner: Ryan
Description: Handles registration, login, JWT, and password reset.
Simplified version: Sends confirmation email on registration (no verification logic).
"""

import os
import secrets
import traceback
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models import User
from app.services.email_service import (
    send_password_reset_email,
    send_confirmation_email,  # ✅ use this new simplified function
)

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


# -------------------- Health --------------------
@auth_bp.route("/")
def home():
    return jsonify({"message": "Auth routes online"}), 200

@auth_bp.route("/test")
def test():
    return jsonify({"message": "Test route works!"}), 200


# -------------------- Register --------------------
@auth_bp.post("/register")
def register():
    """Register client/freelancer/admin (multipart for optional CV)."""
    try:
        current_app.logger.info(f"/register form: {list(request.form.keys())}")
        current_app.logger.info(f"/register files: {list(request.files.keys())}")

        data = request.form
        file = request.files.get("cv")

        required = ["email", "password", "role", "first_name", "last_name"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 409

        # Create user
        user = User(
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
            role=data["role"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            is_active=True,
            is_verified=True,
        )
        db.session.add(user)
        db.session.flush()
        current_app.logger.info(f"Created user {user.email} ({user.role})")

        # Handle CV upload and create FreelancerProfile for freelancers
        if file and user.role == "freelancer":
            current_app.logger.info(f"Processing CV for freelancer: {file.filename}")

            allowed_extensions = {'pdf', 'doc', 'docx'}
            file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                return jsonify({"error": "Only PDF, DOC, and DOCX files are allowed"}), 400

            upload_dir = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            import uuid
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)

            try:
                from app.models.freelancer_profile import FreelancerProfile
                profile = FreelancerProfile(
                    user_id=user.id,
                    name=f"{user.first_name} {user.last_name}",
                    email=user.email,
                    cv_filename=filename,
                    cv_url=f"/uploads/{unique_filename}",
                    cv_uploaded_at=datetime.utcnow(),
                    application_status="pending",
                    open_to_work=True,
                    bio="",
                    hourly_rate=0.0,
                    years_experience=0
                )
                db.session.add(profile)
                current_app.logger.info(f"Created FreelancerProfile for user {user.id}")
            except Exception as e:
                current_app.logger.error(f"Failed to create FreelancerProfile: {str(e)}")
                pass

        # Commit all changes
        db.session.commit()

        # ✅ Send confirmation email (no token)
        try:
            send_confirmation_email(user)
            current_app.logger.info(f"✅ Confirmation email sent to {user.email}")
        except Exception as e:
            current_app.logger.error(f"❌ Failed to send confirmation email: {str(e)}")

        return jsonify({
            "message": "User registered successfully.",
            "user": user.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"REGISTER CRASH: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": "Registration failed"}), 500


# -------------------- Login --------------------
@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email, password = data.get("email"), data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    user.last_login = datetime.utcnow()
    db.session.commit()

    # Send login notification email (optional)
    try:
        from app.services.email_service import send_login_notification_email
        send_login_notification_email(user)
    except Exception as e:
        current_app.logger.error(f"❌ Failed to send login email to {user.email}: {str(e)}")

    claims = {"role": user.role, "email": user.email}
    access = create_access_token(identity=user, additional_claims=claims, expires_delta=timedelta(hours=3))
    refresh = create_refresh_token(identity=user)

    return jsonify({
        "user": user.to_dict(),
        "access_token": access,
        "refresh_token": refresh
    }), 200


# -------------------- Refresh Token --------------------
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        claims = {"role": user.role, "email": user.email}
        new_access = create_access_token(identity=user, additional_claims=claims, expires_delta=timedelta(hours=3))
        return jsonify({"access_token": new_access}), 200

    except Exception as e:
        current_app.logger.error(f"Refresh token error: {e}")
        return jsonify({"error": "Token refresh failed"}), 500


# -------------------- Current User --------------------
@auth_bp.get("/me")
@jwt_required()
def me():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


# -------------------- Reset Password --------------------
@auth_bp.post("/reset-password")
def reset_password():
    data = request.get_json() or {}
    email = data.get("email")
    token = data.get("token")
    new_password = data.get("new_password")

    if email and not token:
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Email not found"}), 404

        user.reset_token = secrets.token_urlsafe(32)
        user.reset_token_expires = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()

        send_password_reset_email(user)
        return jsonify({"message": "Password reset email sent"}), 200

    if token and new_password:
        user = User.query.filter_by(reset_token=token).first()
        if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return jsonify({"error": "Invalid or expired token"}), 400

        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        return jsonify({"message": "Password reset successful"}), 200

    return jsonify({"error": "Invalid request"}), 400


# -------------------- Serve Uploaded CVs --------------------
@auth_bp.route("/uploads/<filename>")
def serve_uploaded_file(filename: str):
    upload_dir = os.path.join(os.getcwd(), "uploads")
    return send_from_directory(upload_dir, filename)
