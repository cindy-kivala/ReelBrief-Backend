"""
Feedback Resource - Structured Revision Requests
Owner: Cindy
Description: Submit and manage feedback on deliverables
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

feedback_bp = Blueprint('feedback', __name__)

# TODO: Cindy - Implement feedback endpoints
#
# Required endpoints:
#
# GET /api/deliverables/:deliverable_id/feedback
# - Requires: JWT auth
# - Return: all feedback for this deliverable
# - Include nested replies (threaded comments)
#
# POST /api/feedback
# - Requires: JWT auth
# - Accept: deliverable_id, feedback_type, content, priority, parent_feedback_id
# - Create feedback record
# - Send notification if it's a new revision request
# - Return: created feedback
#
# PATCH /api/feedback/:id/resolve
# - Requires: JWT auth
# - Update is_resolved to True
# - Set resolved_at timestamp
# - Return: updated feedback
#
# DELETE /api/feedback/:id
# - Requires: JWT auth (feedback author or admin)
# - Delete feedback (or soft delete)
# - Return: success message
#
# Example:
# @feedback_bp.route('/', methods=['POST'])
# @jwt_required()
# def create_feedback():
#     # ... implementation
#     return jsonify(feedback.to_dict()), 201