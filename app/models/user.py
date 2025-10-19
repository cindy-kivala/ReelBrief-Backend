"""
User Model - Authentication & RBAC
Owner: Ryan
Description: Handles user authentication, roles (admin/freelancer/client), and profile data
"""

from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

# TODO: Ryan - Implement User model
#
# Required fields:
# - id (Primary Key)
# - email (Unique, Not Null)
# - password_hash (Not Null)
# - role (admin, freelancer, client)
# - first_name, last_name
# - phone, avatar_url
# - is_active, is_verified
# - verification_token
# - created_at, updated_at, last_login
#
# Relationships:
# - freelancer_profile (one-to-one)
# - projects_as_client (one-to-many)
# - projects_as_freelancer (one-to-many)
# - notifications (one-to-many)
#
# Methods:
# - set_password(password)
# - check_password(password)
# - to_dict()
#
# Example structure:
# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     # ... rest of fields


# Ryan you'll always the the first to merge and we'll continue in that order
