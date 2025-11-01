"""
Authentication Resource - Auth Endpoints
Owner: Ryan
Description:
  Handles registration (with optional freelancer CV upload), login with JWT,
  optional email verification (auto-verify toggle), refresh, current user (me),
  and password reset. Also alerts admin on freelancer CV submission.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from flask import Blueprint, jsonify, request, send_from_directory

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
    send_admin_freelancer_application_email,
)

try:
    from app.models.freelancer_profile import FreelancerProfile
except Exception:
    FreelancerProfile = None

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

AUTO_VERIFY_EMAILS = os.getenv("AUTO_VERIFY_EMAILS", "true").lower() == "true"
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")


@auth_bp.route("/")
def auth_home():
    """Simple liveness probe for auth routes."""
    return jsonify({"message": "Auth routes are working!"}), 200


@auth_bp.route("/test")
def test():
    """Tiny test route for quick checks."""
    return jsonify({"message": "Test route works!"}), 200


@auth_bp.post("/register")
def register():
    """
    Register a user (client, freelancer, or admin).
    Accepts multipart/form-data to support optional CV upload for freelancers (field name: 'cv').
    """
    try:
        print("📥 /register form keys:", list(request.form.keys()))
        print("📎 /register files:", list(request.files.keys()))

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
        print(f"✅ Created user {user.email} ({user.role})")

        if file and user.role == "freelancer":
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            file_path = os.path.join(UPLOAD_DIR, file.filename)
            file.save(file_path)
            print(f"📄 CV saved to {file_path}")

            profile_obj: Optional[object] = None
            if FreelancerProfile is not None:
                try:
                    profile_obj = FreelancerProfile(
                        user_id=user.id,
                        cv_filename=file.filename,
                        cv_url=f"/uploads/{file.filename}",
                        cv_uploaded_at=datetime.utcnow(),
                        application_status="pending",
                    )
                    db.session.add(profile_obj)
                    db.session.commit()
                    print("🧾 FreelancerProfile created (pending)")
                except Exception as e:
                    print(f"⚠️ Could not create FreelancerProfile: {e}")

            try:
                sent_admin = send_admin_freelancer_application_email(user, profile_obj)
                print(f"📨 Admin alert about freelancer CV sent? {sent_admin}")
            except Exception as e:
                print(f"⚠️ Admin alert email failed: {e}")

        if AUTO_VERIFY_EMAILS:
            user.is_verified = True
            user.is_active = True
            user.verification_token = None
            db.session.commit()
            print("✅ AUTO_VERIFY_EMAILS=true → user auto-verified.")
        else:
            try:
                ok, token = send_verification_email(user.email, user.id)
                user.verification_token = token
                db.session.commit()
                print(f"✉️ Verification email → {user.email} | sent={ok}")
            except Exception as e:
                print(f"⚠️ Verification email failed: {e}")

        return jsonify({"message": "User registered successfully."}), 201

    except Exception as e:
        print("🔥 REGISTER CRASH:", e)
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.post("/login")
def login():
    """
    Log in a user by email/password.
    Returns access and refresh JWT tokens plus a sanitized user object.
    Blocks unverified users unless AUTO_VERIFY_EMAILS is on (they will be verified at register).
    """
    data = request.get_json() or {}
    email, password = data.get("email"), data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    claims = {"role": user.role, "email": user.email}
    access = create_access_token(identity=user.id, additional_claims=claims, expires_delta=timedelta(hours=3))
    refresh = create_refresh_token(identity=user.id)

    return jsonify({
        "user": user.to_dict(),
        "access_token": access,
        "refresh_token": refresh,
    }), 200


@auth_bp.post("/verify-email")
def verify_email():
    """
    Verify user with a token (emailed to them).
    Only used when AUTO_VERIFY_EMAILS=false and you send real emails.
    """
    data = request.get_json() or {}
    token = data.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY", "devsecretkey"))
    try:
        user_id = serializer.loads(token, salt="email-verify", max_age=3600)
    except SignatureExpired:
        return jsonify({"error": "Token expired"}), 400
    except BadSignature:
        return jsonify({"error": "Invalid token"}), 400

    user = User.query.get(user_id)
    if not user or (getattr(user, "verification_token", None) and user.verification_token != token):
        return jsonify({"error": "Invalid or already used token"}), 404

    user.is_verified = True
    user.is_active = True
    user.verification_token = None
    db.session.commit()

    print(f"✅ Verified email for {user.email}")
    return jsonify({"message": "Email verified successfully"}), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """
    Exchange a refresh token for a new access token.
    """
    current_user_id = get_jwt_identity()
    new_access = create_access_token(identity=current_user_id, expires_delta=timedelta(hours=3))
    return jsonify({"access_token": new_access}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    """
    Get the current authenticated user's profile.
    """
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


@auth_bp.post("/reset-password")
def reset_password():
    """
    Two-step password reset flow:
      1) Request: { "email": "user@example.com" }
      2) Confirm: { "token": "<reset_token>", "new_password": "..." }
    """
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


@auth_bp.route("/uploads/<filename>")
def serve_uploaded_file(filename: str):
    """
    Serve uploaded freelancer CVs from the uploads directory.
    In production you should use a proper static file server or cloud storage.
    """
    return send_from_directory(UPLOAD_DIR, filename)