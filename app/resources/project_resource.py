"""
Project Resource - Project Management Endpoints
Owner: Monica
Description: CRUD operations for projects + assignment logic
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.project import Project
from app.extensions import db
project_bp = Blueprint('projects', __name__)

@project_bp.route('/', methods=['GET'])

# TODO: Monica - Implement project endpoints
#
# Required endpoints:
#
# GET /api/projects
# - Requires: JWT auth
# - Query params: page, per_page, status, client_id, freelancer_id
# - Return: paginated list of projects
# - Filter based on user role:
#   - Admin: sees all projects
#   - Freelancer: sees only assigned projects
#   - Client: sees only their projects
#
# GET /api/projects/:id
# - Requires: JWT auth
# - Return: project details with related data
# - Authorization: check user has access to this project
#
# POST /api/projects
# - Requires: JWT auth (client or admin)
# - Accept: title, description, budget, deadline, project_type, is_sensitive, required_skills
# - Create project with status='submitted'
# - Return: created project
#
# PATCH /api/projects/:id
# - Requires: JWT auth
# - Accept: any project fields to update
# - Authorization: only admin or project owner
# - Return: updated project
#
# DELETE /api/projects/:id
# - Requires: JWT auth (admin only)
# - Soft delete or mark as cancelled
# - Return: success message
#
# POST /api/projects/:id/assign-freelancer
# - Requires: JWT auth (admin only)
# - Accept: freelancer_id
# - Check freelancer availability (open_to_work=True)
# - Update project status to 'matched'
# - Send notification to freelancer
# - Return: updated project
#
# POST /api/projects/:id/complete
# - Requires: JWT auth (admin or client)
# - Update status to 'completed'
# - Trigger portfolio generation (if not is_sensitive)
# - Return: success message
#
# Example:
# @project_bp.route('/', methods=['GET'])
# @jwt_required()
# def get_projects():
#     # ... implementation with pagination
#     return jsonify({'projects': [], 'pagination': {}}), 200
