"""
Authentication Resource - Auth Endpoints
Owner: Ryan
Description: User registration, login, email verification, password reset
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

auth_bp = Blueprint("auth", __name__)

# TODO: Ryan - Implement authentication endpoints
#
# Required endpoints:
#
# POST /api/auth/register
# - Accept: email, password, role, first_name, last_name
# - Validate input (email format, password strength)
# - Hash password with werkzeug
# - Create user with is_active=False
# - Generate verification_token
# - Send verification email via email_service
# - Return: user data (no password) + message
#
# POST /api/auth/login
# - Accept: email, password
# - Verify credentials
# - Check if user is_active and is_verified
# - Create JWT access token
# - Update last_login timestamp
# - Return: access_token, user data
#
# POST /api/auth/verify-email
# - Accept: token (from email link)
# - Find user by verification_token
# - Set is_verified=True, is_active=True
# - Clear verification_token
# - Return: success message
#
# GET /api/auth/me
# - Requires: JWT token in Authorization header
# - Get current user from get_jwt_identity()
# - Return: current user data
#
# POST /api/auth/reset-password
# - Accept: email (step 1) or token + new_password (step 2)
# - Step 1: Generate reset token, send email
# - Step 2: Verify token, update password
# - Return: success message
#
# Example:
# @auth_bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     # ... implementation
#     return jsonify({'message': 'User registered'}), 201
