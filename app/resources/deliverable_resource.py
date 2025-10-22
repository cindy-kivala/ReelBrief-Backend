"""
Deliverable Resource - File Upload & Version Control
Owner: Cindy
Description: Upload files, track versions, manage deliverable lifecycle
"""

from flask import Blueprint, jsonify, request, current_app
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

@deliverable_bp.route('/<int:deliverable_id>', methods=['GET'])
@jwt_required()
def get_deliverable(deliverable_id):
    """Get specific deliverable with metadata and feedback"""
    try:
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        
        return jsonify({
            'success': True,
            'deliverable': deliverable.to_dict(include_feedback=True)
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Deliverable not found'}), 404

#
# POST /api/deliverables
# - Requires: JWT auth (freelancer only)
# - Accept: project_id, title, description, file (multipart/form-data), change_notes
# - Upload file to Cloudinary via cloudinary_service
# - Auto-increment version_number for this project
# - Create deliverable record with file_url, cloudinary_public_id
# - Send notification to client
# - Return: created deliverable
@deliverable_bp.route('/', methods=['POST'])
@jwt_required()
# @role_required('freelancer')  # Uncomment when Ryan creates decorator
def create_deliverable():
    """
    Upload new deliverable with file
    
    Form data:
        - file: File to upload (required)
        - project_id: Project ID (required)
        - title: Deliverable title
        - description: Description
        - change_notes: What changed from previous version
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Validate request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Get form data
        project_id = request.form.get('project_id', type=int)
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        change_notes = request.form.get('change_notes', '')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Project ID is required'}), 400
        
        # Validate file type
        if not CloudinaryService.allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        # Determine file type
        file_type = CloudinaryService.get_file_type(file.filename)
        
        # Upload to Cloudinary
        folder = f'reelbrief/project_{project_id}'
        upload_result = CloudinaryService.upload_file(file, folder=folder)
        
        if not upload_result['success']:
            return jsonify({
                'success': False,
                'error': 'File upload failed',
                'details': upload_result.get('error')
            }), 500
        
        # Get next version number
        version_number = Deliverable.get_next_version_number(project_id)
        
        # Create deliverable record
        deliverable = Deliverable(
            project_id=project_id,
            version_number=version_number,
            file_url=upload_result['url'],
            file_type=file_type,
            file_size=upload_result.get('bytes'),
            cloudinary_public_id=upload_result['public_id'],
            thumbnail_url=upload_result.get('thumbnail_url'),
            title=title or f"Version {version_number}",
            description=description,
            change_notes=change_notes,
            uploaded_by=current_user_id,
            status='pending'
        )
        
        db.session.add(deliverable)
        db.session.commit()
        
        # REMEMBER!!!!: Send notification to client (when Ryan creates notification service)-Already existss 
        # in an upcoming comit wok on that notification or email serveice
        
        return jsonify({
            'success': True,
            'message': 'Deliverable uploaded successfully',
            'deliverable': deliverable.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create deliverable'}), 500

#
# PATCH /api/deliverables/:id
# - Requires: JWT auth
# - Accept: title, description (metadata updates)
# - Return: updated deliverable
@deliverable_bp.route('/<int:deliverable_id>', methods=['PATCH'])
@jwt_required()
def update_deliverable(deliverable_id):
    """
    Update deliverable metadata (not the file itself)
    
    JSON body:
        - title: New title
        - description: New description
    """
    try:
        current_user_id = get_jwt_identity()
        
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        
        # Check ownership (freelancer who uploaded it)
        if deliverable.uploaded_by != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            deliverable.title = data['title']
        
        if 'description' in data:
            deliverable.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deliverable updated successfully',
            'deliverable': deliverable.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update deliverable'}), 500
    
@deliverable_bp.route('/<int:deliverable_id>', methods=['DELETE'])
@jwt_required()
def delete_deliverable(deliverable_id):
    """Delete a deliverable (soft delete - mark as rejected)"""
    try:
        current_user_id = get_jwt_identity()
        
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        
        # Check ownership or admin
        # if deliverable.uploaded_by != current_user_id and current_user.role != 'admin':
        #     return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Delete from Cloudinary
        if deliverable.cloudinary_public_id:
            CloudinaryService.delete_file(
                deliverable.cloudinary_public_id,
                resource_type='image'  # Adjust based on file_type
            )
        
        # Delete from database
        db.session.delete(deliverable)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deliverable deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to delete deliverable'}), 500


#
# GET /api/deliverables/:id/versions
# - Requires: JWT auth
# - Return: all versions of this deliverable (by project_id)
# - Useful for version comparison

@deliverable_bp.route('/<int:deliverable_id>/versions', methods=['GET'])
@jwt_required()
def get_deliverable_versions(deliverable_id):
    """Get all versions of a deliverable (by project)"""
    try:
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        project_id = deliverable.project_id
        
        # Get all deliverables for this project
        versions = Deliverable.query.filter_by(project_id=project_id).order_by(
            Deliverable.version_number.asc()
        ).all()
        
        return jsonify({
            'success': True,
            'versions': [v.to_dict(include_feedback=False) for v in versions],
            'total_versions': len(versions)
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching versions: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch versions'}), 500

#
# POST /api/deliverables/:id/approve
# - Requires: JWT auth (client or admin)
# - Update status to 'approved'
# - Set reviewed_at, reviewed_by
# - Trigger payment release if final deliverable
# - Return: updated deliverable

"""
Deliverable Resource - File Upload & Version Control
Owner: Cindy
Description: Upload files, track versions, manage deliverable lifecycle
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.deliverable import Deliverable
from app.models.user import User
from app.services.cloudinary_service import CloudinaryService
# from app.utils.decorators import role_required  # Ryan will create this

deliverable_bp = Blueprint("deliverables", __name__, url_prefix='/api/deliverables')


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


@deliverable_bp.route('/<int:deliverable_id>', methods=['GET'])
@jwt_required()
def get_deliverable(deliverable_id):
    """Get specific deliverable with metadata and feedback"""
    try:
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        
        return jsonify({
            'success': True,
            'deliverable': deliverable.to_dict(include_feedback=True)
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Deliverable not found'}), 404


@deliverable_bp.route('/', methods=['POST'])
@jwt_required()
# @role_required('freelancer')  # Uncomment when Ryan creates decorator
def create_deliverable():
    """
    Upload new deliverable with file
    
    Form data:
        - file: File to upload (required)
        - project_id: Project ID (required)
        - title: Deliverable title
        - description: Description
        - change_notes: What changed from previous version
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Validate request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Get form data
        project_id = request.form.get('project_id', type=int)
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        change_notes = request.form.get('change_notes', '')
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Project ID is required'}), 400
        
        # Validate file type
        if not CloudinaryService.allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        # Determine file type
        file_type = CloudinaryService.get_file_type(file.filename)
        
        # Upload to Cloudinary
        folder = f'reelbrief/project_{project_id}'
        upload_result = CloudinaryService.upload_file(file, folder=folder)
        
        if not upload_result['success']:
            return jsonify({
                'success': False,
                'error': 'File upload failed',
                'details': upload_result.get('error')
            }), 500
        
        # Get next version number
        version_number = Deliverable.get_next_version_number(project_id)
        
        # Create deliverable record
        deliverable = Deliverable(
            project_id=project_id,
            version_number=version_number,
            file_url=upload_result['url'],
            file_type=file_type,
            file_size=upload_result.get('bytes'),
            cloudinary_public_id=upload_result['public_id'],
            thumbnail_url=upload_result.get('thumbnail_url'),
            title=title or f"Version {version_number}",
            description=description,
            change_notes=change_notes,
            uploaded_by=current_user_id,
            status='pending'
        )
        
        db.session.add(deliverable)
        db.session.commit()
        
        # TODO: Send notification to client (when Caleb creates notification service)
        
        return jsonify({
            'success': True,
            'message': 'Deliverable uploaded successfully',
            'deliverable': deliverable.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create deliverable'}), 500


@deliverable_bp.route('/<int:deliverable_id>', methods=['PATCH'])
@jwt_required()
def update_deliverable(deliverable_id):
    """
    Update deliverable metadata (not the file itself)
    
    JSON body:
        - title: New title
        - description: New description
    """
    try:
        current_user_id = get_jwt_identity()
        
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        
        # Check ownership (freelancer who uploaded it)
        if deliverable.uploaded_by != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            deliverable.title = data['title']
        
        if 'description' in data:
            deliverable.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deliverable updated successfully',
            'deliverable': deliverable.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update deliverable'}), 500


@deliverable_bp.route('/<int:deliverable_id>', methods=['DELETE'])
@jwt_required()
def delete_deliverable(deliverable_id):
    """Delete a deliverable (soft delete - mark as rejected)"""
    try:
        current_user_id = get_jwt_identity()
        
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        
        # Check ownership or admin
        # if deliverable.uploaded_by != current_user_id and current_user.role != 'admin':
        #     return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Delete from Cloudinary
        if deliverable.cloudinary_public_id:
            CloudinaryService.delete_file(
                deliverable.cloudinary_public_id,
                resource_type='image'  # Adjust based on file_type
            )
        
        # Delete from database
        db.session.delete(deliverable)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deliverable deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to delete deliverable'}), 500


@deliverable_bp.route('/<int:deliverable_id>/versions', methods=['GET'])
@jwt_required()
def get_deliverable_versions(deliverable_id):
    """Get all versions of a deliverable (by project)"""
    try:
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        project_id = deliverable.project_id
        
        # Get all deliverables for this project
        versions = Deliverable.query.filter_by(project_id=project_id).order_by(
            Deliverable.version_number.asc()
        ).all()
        
        return jsonify({
            'success': True,
            'versions': [v.to_dict(include_feedback=False) for v in versions],
            'total_versions': len(versions)
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching versions: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch versions'}), 500


@deliverable_bp.route('/<int:deliverable_id>/approve', methods=['POST'])
@jwt_required()
@role_required(['client', 'admin'])
def approve_deliverable(deliverable_id):
    """
    Approve a deliverable
    
    Triggers:
        - Update status to 'approved'
        - Set reviewed_by and reviewed_at
        - Trigger payment release (if final deliverable)
        - Send notification to freelancer
    """
    try:
        current_user_id = get_jwt_identity()
        
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        
        # Check if already approved
        if deliverable.status == 'approved':
            return jsonify({
                'success': False,
                'error': 'Deliverable already approved'
            }), 400
        
        # Approve deliverable
        deliverable.approve(reviewed_by_id=current_user_id)
        
        # TODO: Trigger payment release (when Caleb creates escrow service)
        # TODO: Send notification to freelancer (when Ryan creates notification service)
        
        return jsonify({
            'success': True,
            'message': 'Deliverable approved successfully',
            'deliverable': deliverable.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving deliverable: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to approve deliverable'}), 500

#
# POST /api/deliverables/:id/request-revision
# - Requires: JWT auth (client or admin)
# - Accept: feedback content, priority, deadline
# - Update status to 'revision_requested'
# - Create feedback record
# - Send notification to freelancer
# - Return: deliverable + feedback