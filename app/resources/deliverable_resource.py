"""
Deliverable Resource - File Upload & Version Control
Owner: Cindy
Description: Upload files, track versions, manage deliverable lifecycle
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.deliverable import Deliverable
from app.models.user import User
from app.services.cloudinary_service import CloudinaryService
from app.utils.decorators import role_required

deliverable_bp = Blueprint("deliverables", __name__, url_prefix="/api/deliverables")

# Required endpoints:
#
# GET /api/projects/:project_id/deliverables
# - Requires: JWT auth
# - Query params: page, per_page
# - Return: all deliverables for project (all versions)
# - Group by version or return flat list
@deliverable_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_deliverables(project_id):
    """
    Get all deliverables for a project
    
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 10)
        - version: Filter by specific version
        - status: Filter by status
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Filters
        version = request.args.get('version', type=int)
        status = request.args.get('status', type=str)
        
        # Build query
        query = Deliverable.query.filter_by(project_id=project_id)
        
        if version:
            query = query.filter_by(version_number=version)
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by version and upload date
        query = query.order_by(Deliverable.version_number.desc(), Deliverable.uploaded_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        deliverables = [d.to_dict(include_feedback=False) for d in pagination.items]
        
        return jsonify({
            'success': True,
            'deliverables': deliverables,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total_pages': pagination.pages,
                'total_items': pagination.total
            }
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching deliverables: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch deliverables'}), 500
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
