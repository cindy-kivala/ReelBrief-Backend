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
            is_active=False,
            is_verified=False,
        )
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        current_app.logger.info(f"Created user {user.email} ({user.role})")

        # Handle CV upload and create FreelancerProfile for freelancers
        if file and user.role == "freelancer":
            current_app.logger.info(f"Processing CV for freelancer: {file.filename}")
            
            # Validate file type
            allowed_extensions = {'pdf', 'doc', 'docx'}
            file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            
            if file_ext not in allowed_extensions:
                return jsonify({"error": "Only PDF, DOC, and DOCX files are allowed"}), 400

            # Create uploads directory
            upload_dir = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            import uuid
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Create FreelancerProfile with CV data
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
                    bio="",  # Can be updated later
                    hourly_rate=0.0,  # Default, can be updated later
                    years_experience=0  # Default, can be updated later
                )
                db.session.add(profile)
                current_app.logger.info(f"Created FreelancerProfile for user {user.id}")
            except Exception as e:
                current_app.logger.error(f" Failed to create FreelancerProfile: {str(e)}")
                # Don't fail registration if profile creation fails
                pass

        # Commit everything
        db.session.commit()

        # Send verification email
        ok, token = send_verification_email(user.email, user.id)
        user.verification_token = token
        db.session.commit()
        
        current_app.logger.info(f" Verification email → {user.email} | sent={ok}")

        # Return success response
        dev_url = f"{os.getenv('BASE_URL', 'http://localhost:5174')}/verify-email/{token}"
        return jsonify({
            "message": "User registered successfully.",
            "user": user.to_dict(),
            "dev_verify_url": dev_url,
            "verification_token": token
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f" REGISTER CRASH: {str(e)}")
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

    # if not user.is_verified:
    #     return jsonify({"error": "Email not verified"}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    claims = {"role": user.role, "email": user.email}
    
    # Pass the User OBJECT to create_access_token
    # The user_identity_lookup will extract the ID from it
    access = create_access_token(
        identity=user,  # Pass the User object, not just the ID
        additional_claims=claims, 
        expires_delta=timedelta(hours=3)
    )
    refresh = create_refresh_token(identity=user)  # Also pass User object

    return jsonify({
        "user": user.to_dict(), 
        "access_token": access, 
        "refresh_token": refresh
    }), 200
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
    """Refresh access token - fixed to handle new identity format"""
    try:
        current_user_id = get_jwt_identity()
        
        # current_user_id should be the user ID (integer)
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        claims = {"role": user.role, "email": user.email}
        
        # Pass the User OBJECT to create_access_token
        new_access = create_access_token(
            identity=user,  # Pass User object
            additional_claims=claims, 
            expires_delta=timedelta(hours=3)
        )
        
        return jsonify({"access_token": new_access}), 200
        
    except Exception as e:
        print(f"Refresh token error: {e}")
        return jsonify({"error": "Token refresh failed"}), 500


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
