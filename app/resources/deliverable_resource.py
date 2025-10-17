"""
Deliverable Resource - File Upload & Version Control
Owner: Cindy
Description: Upload files, track versions, manage deliverable lifecycle
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

deliverable_bp = Blueprint('deliverables', __name__)

# TODO: Cindy - Implement deliverable endpoints
#
# Required endpoints:
#
# GET /api/projects/:project_id/deliverables
# - Requires: JWT auth
# - Query params: page, per_page
# - Return: all deliverables for project (all versions)
# - Group by version or return flat list
#
# GET /api/deliverables/:id
# - Requires: JWT auth
# - Return: specific deliverable with metadata
# - Include feedback if any
#
# POST /api/deliverables
# - Requires: JWT auth (freelancer only)
# - Accept: project_id, title, description, file (multipart/form-data), change_notes
# - Upload file to Cloudinary via cloudinary_service
# - Auto-increment version_number for this project
# - Create deliverable record with file_url, cloudinary_public_id
# - Send notification to client
# - Return: created deliverable
#
# PATCH /api/deliverables/:id
# - Requires: JWT auth
# - Accept: title, description (metadata updates)
# - Return: updated deliverable
#
# POST /api/deliverables/:id/approve
# - Requires: JWT auth (client or admin)
# - Update status to 'approved'
# - Set reviewed_at, reviewed_by
# - Trigger payment release if final deliverable
# - Return: updated deliverable
#
# POST /api/deliverables/:id/request-revision
# - Requires: JWT auth (client or admin)
# - Accept: feedback content, priority, deadline
# - Update status to 'revision_requested'
# - Create feedback record
# - Send notification to freelancer
# - Return: deliverable + feedback
#
# GET /api/deliverables/:id/versions
# - Requires: JWT auth
# - Return: all versions of this deliverable (by project_id)
# - Useful for version comparison
#
# Example:
# @deliverable_bp.route('/', methods=['POST'])
# @jwt_required()
# def create_deliverable():
#     # ... implementation with Cloudinary upload
#     return jsonify(deliverable.to_dict()), 201