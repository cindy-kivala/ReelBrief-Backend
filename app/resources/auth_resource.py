"""
Authentication Resource - Auth Endpoints
Owner: Ryan
Description: Handles registration, login, JWT, email verification, and password reset.
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
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.extensions import db
from app.models import User
from app.services.email_service import (
    send_password_reset_email,
    send_verification_email,
)

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


# -------------------- Health --------------------
@auth_bp.route("/")
def home():
    return jsonify({"message": "🎬 Auth routes online"}), 200

@auth_bp.route("/test")
def test():
    return jsonify({"message": "Test route works!"}), 200


# -------------------- Register --------------------
@auth_bp.post("/register")
def register():
    """Register client/freelancer/admin (multipart for optional CV)."""
    try:
        current_app.logger.info(f"📥 /register form: {list(request.form.keys())}")
        current_app.logger.info(f"📎 /register files: {list(request.files.keys())}")

        data = request.form
        file = request.files.get("cv")

        required = ["email", "password", "role", "first_name", "last_name"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 409

        user = User(
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
            role=data["role"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            is_active=False,
            is_verified=False,
        )
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"✅ Created user {user.email} ({user.role})")

        # Optional CV upload
        if file and user.role == "freelancer":
            upload_dir = os.path.join(os.getcwd(), "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, file.filename)
            file.save(file_path)
            current_app.logger.info(f"📄 CV saved to {file_path}")

            # Optional: create FreelancerProfile if model exists
            try:
                from app.models.freelancer_profile import FreelancerProfile
                profile = FreelancerProfile(
                    user_id=user.id,
                    cv_filename=file.filename,
                    cv_url=f"/uploads/{file.filename}",
                    cv_uploaded_at=datetime.utcnow(),
                    application_status="pending",
                )
                db.session.add(profile)
                db.session.commit()
            except Exception as e:
                current_app.logger.warning(f"⚠️ Could not create FreelancerProfile: {e}")

        # Send verification email (returns ok + token)
        ok, token = send_verification_email(user.email, user.id)
        user.verification_token = token
        db.session.commit()
        current_app.logger.info(f"✉️ Verification email → {user.email} | sent={ok}")

        # ✅ Dev convenience: always return a verify URL + token so you can proceed even if email fails
        dev_url = f"{os.getenv('BASE_URL', 'http://localhost:5174')}/verify-email/{token}"
        payload = {
            "message": "User registered successfully.",
            "dev_verify_url": dev_url,
            "verification_token": token
        }
        return jsonify(payload), 201

    except Exception:
        current_app.logger.error("🔥 REGISTER CRASH:\n" + traceback.format_exc())
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

    # if not user.is_verified:
    #     return jsonify({"error": "Email not verified"}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    claims = {"role": user.role, "email": user.email}
    access = create_access_token(identity=user.id, additional_claims=claims, expires_delta=timedelta(hours=3))
    refresh = create_refresh_token(identity=user.id)

    return jsonify({"user": user.to_dict(), "access_token": access, "refresh_token": refresh}), 200


# -------------------- Verify Email --------------------
@auth_bp.post("/verify-email")
def verify_email():
    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    serializer = URLSafeTimedSerializer(current_app.config.get("SECRET_KEY", "devsecretkey"))
    try:
        user_id = serializer.loads(token, salt="email-verify", max_age=3600)
    except SignatureExpired:
        return jsonify({"error": "Token expired"}), 400
    except BadSignature:
        return jsonify({"error": "Invalid token"}), 400

    user = User.query.get(user_id)
    if not user or user.verification_token != token:
        return jsonify({"error": "Invalid or already used token"}), 404

    user.is_verified = True
    user.is_active = True
    user.verification_token = None
    db.session.commit()

    current_app.logger.info(f"✅ Verified email for {user.email}")
    return jsonify({"message": "Email verified successfully"}), 200


# -------------------- Refresh --------------------
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access = create_access_token(identity=current_user, expires_delta=timedelta(hours=3))
    return jsonify({"access_token": new_access}), 200


# -------------------- Current user --------------------
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

    # Request reset
    if email and not token:
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Email not found"}), 404

        user.reset_token = secrets.token_urlsafe(32)
        user.reset_token_expires = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()

        send_password_reset_email(user)
        return jsonify({"message": "Password reset email sent"}), 200

    # Confirm reset
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


# -------------------- Serve uploaded CVs --------------------
@auth_bp.route("/uploads/<filename>")
def serve_uploaded_file(filename: str):
    upload_dir = os.path.join(os.getcwd(), "uploads")
    return send_from_directory(upload_dir, filename)
