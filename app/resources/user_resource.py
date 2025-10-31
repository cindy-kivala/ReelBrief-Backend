"""
User Resource - User Profile Management
Owner: Ryan
Description: Get and update user profiles
"""

"""
User Resource - User Profile Management
Owner: Ryan
Description: Get and update user profiles
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.extensions import db
from app.utils.decorators import role_required  # ✅ FIXED PATH
from app.schemas.user_schema import user_schema, users_schema



user_bp = Blueprint("user_bp", __name__)

# -------------------- GET USER BY ID --------------------
@user_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])
    
    if not user or user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # returning user data properly
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# @jwt_required()
# def get_user(id):
#     """
#     Get a user's profile by ID.
#     Only the user themselves or an admin can access this.
#     """
#     current_user_id = get_jwt_identity()
#     current_user = User.query.get(current_user_id)

#     if not current_user:
#         return jsonify({"error": "Unauthorized"}), 401

#     user = User.query.get_or_404(id)

#     # Non-admins can only view their own profile
#     if current_user.id != user.id and current_user.role != "admin":
#         return jsonify({"error": "You are not authorized to view this profile"}), 403

#     return jsonify(user.to_dict()), 200


# -------------------- UPDATE USER PROFILE --------------------
@user_bp.route("/<int:id>", methods=["PATCH"])
@jwt_required()
def update_user(id):
    """
    Update user profile fields.
    Allowed fields: first_name, last_name, phone, avatar_url, bio
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get_or_404(id)

    # Authorization: Only the user or admin can update
    if current_user.id != user.id and current_user.role != "admin":
        return jsonify({"error": "You are not authorized to update this profile"}), 403

    data = request.get_json() or {}

    allowed_fields = ["first_name", "last_name", "phone", "avatar_url", "bio"]
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()

    return jsonify(user.to_dict()), 200


# -------------------- LIST USERS (ADMIN ONLY) --------------------
@user_bp.route("/", methods=["GET"])
@jwt_required()
@role_required(["admin"])
def list_users():
    """
    Admin-only endpoint to list users with pagination.
    """
    from app.services.pagination_service import paginate_query
    from app.schemas.user_schema import users_schema

    query = User.query.order_by(User.created_at.desc())
    result = paginate_query(query)

    return jsonify({
        "data": users_schema.dump(result["items"]),
        "meta": result["meta"]
    }), 200


# TODO: Ryan - Implement user endpoints
#
# Required endpoints:
#
# GET /api/users/:id
# - Requires: JWT auth
# - Get user by ID
# - Return: user data (exclude password_hash)
# - Authorization: Users can only view their own profile (unless admin)
#
# PATCH /api/users/:id
# - Requires: JWT auth
# - Accept: first_name, last_name, phone, avatar_url
# - Update user fields
# - Authorization: Users can only update their own profile (unless admin)
# - Return: updated user data
#
# Example:
# @user_bp.route('/<int:id>', methods=['GET'])
# @jwt_required()
# def get_user(id):
#     # ... implementation
#     return jsonify(user.to_dict()), 200
