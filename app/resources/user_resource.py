"""
User Resource - User Profile Management
Owner: Ryan
Description: Get and update user profiles
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

user_bp = Blueprint("users", __name__)

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
