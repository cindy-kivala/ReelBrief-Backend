"""
Review Resource - Freelancer Reviews & Ratings
Owner: Caleb
Description: Submit and view reviews for completed projects.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

review_bp = Blueprint('reviews', __name__)

# TODO: Caleb - Implement review endpoints
#
# POST /api/reviews
# - Requires: JWT auth (client only)
# - Accept: project_id, rating, communication_rating, quality_rating,
#           timeliness_rating, review_text, is_public
# - Validate: project is completed, client is project owner
# - Create review record
# - Send notification to freelancer
# - Return: created review
#
# GET /api/users/<int:user_id>/reviews
# - Requires: JWT auth
# - Query: page, per_page
# - Return: all reviews for a freelancer (public only unless owner)
#
# GET /api/projects/<int:project_id>/reviews
# - Requires: JWT auth
# - Return: review for this project
#
# PATCH /api/reviews/<int:id>
# - Requires: JWT auth (review author)
# - Update review fields
# - Return: updated review
#
# GET /api/freelancers/<int:freelancer_id>/rating-summary
# - Public or auth
# - Return: average ratings (overall, communication, quality, timeliness)
#
# Example:
# @review_bp.route('/', methods=['POST'])
# @jwt_required()
# def create_review():
#     current_user = get_jwt_identity()
#     data = request.get_json()
#     # Save review
#     return jsonify({'message': 'Review created'}), 201
