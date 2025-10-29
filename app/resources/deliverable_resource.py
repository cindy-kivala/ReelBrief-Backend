"""
Deliverable Resource - File Upload & Version Control
Owner: Cindy
Description: Upload files, track versions, manage deliverable lifecycle
"""
import os
import re
from datetime import datetime, timedelta
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.deliverable import Deliverable
from app.models.user import User
from app.models.project import Project
from app.services.cloudinary_service import CloudinaryService
from app.services.email_service import (
    send_email,
    send_deliverable_approved_notification,
    send_deliverable_feedback_notification
)
from app.utils.decorators import role_required

deliverable_bp = Blueprint("deliverables", __name__, url_prefix="/api/deliverables")

# Constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'}

# Helper functions
def validate_deliverable_data(title, description, change_notes):
    """Validate deliverable input data"""
    if title and len(title) > 200:
        raise ValueError("Title must be less than 200 characters")
    if description and len(description) > 2000:
        raise ValueError("Description must be less than 2000 characters")
    if change_notes and len(change_notes) > 1000:
        raise ValueError("Change notes must be less than 1000 characters")
    
    return title, description, change_notes

def create_portfolio_item(project, deliverable):
    """Helper function to create portfolio item"""
    from app.models.portfolio_item import PortfolioItem
    
    return PortfolioItem(
        freelancer_id=project.freelancer_id,
        project_id=project.id,
        title=project.title,
        description=project.description or f"Completed project: {project.title}",
        deliverables_description=f"Approved deliverable: {deliverable.title}",
        skills_used=getattr(project, 'tags', []) or [],
        project_duration=f"{project.duration} days" if project.duration else "Not specified",
        client_feedback="Project successfully completed and approved",
        is_visible=True,
        featured_image_url=deliverable.thumbnail_url or deliverable.file_url,
        project_url=f"/projects/{project.id}",
        completion_date=datetime.utcnow()
    )

def error_response(message, status_code, details=None):
    """Create consistent error response format"""
    response = {
        "success": False,
        "error": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    if details:
        response["details"] = details
    return jsonify(response), status_code

@deliverable_bp.route("/projects/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project_deliverables(project_id):
    """Get all deliverables for a project"""
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        version = request.args.get("version", type=int)
        status = request.args.get("status", type=str)

        query = Deliverable.query.filter_by(project_id=project_id)

        if version:
            query = query.filter_by(version_number=version)

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(Deliverable.version_number.desc(), Deliverable.uploaded_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        deliverables = [d.to_dict(include_feedback=False) for d in pagination.items]

        return jsonify({
            "success": True,
            "deliverables": deliverables,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total_pages": pagination.pages,
                "total_items": pagination.total,
            },
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching deliverables: {str(e)}")
        return error_response("Failed to fetch deliverables", 500, str(e))

@deliverable_bp.route("/freelancer/my-deliverables", methods=["GET"])
@jwt_required()
def get_my_deliverables():
    """Get all deliverables uploaded by the current freelancer"""
    try:
        current_user_id = get_jwt_identity()
        
        if not current_user_id:
            return error_response("Authentication required", 401)
        
        # Fixed: Using join to avoid N+1 queries
        deliverables = (Deliverable.query
                .join(Project, Deliverable.project_id == Project.id)
                .filter(Deliverable.uploaded_by == current_user_id)
                .add_columns(Project.title)
                .order_by(Deliverable.project_id, Deliverable.version_number.desc())
                .all())

        result = []
        for deliverable, project_title in deliverables:
            deliverable_dict = deliverable.to_dict(include_feedback=False)
            deliverable_dict['project_title'] = project_title
            result.append(deliverable_dict)
        
        return jsonify({
            "success": True,
            "deliverables": result,
            "total": len(result)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching freelancer deliverables: {str(e)}")
        return error_response("Failed to fetch deliverables", 500, str(e))

@deliverable_bp.route("/<int:deliverable_id>", methods=["GET"])
@jwt_required()
def get_deliverable(deliverable_id):
    """Get specific deliverable with metadata and feedback"""
    try:
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        return jsonify({
            "success": True, 
            "deliverable": deliverable.to_dict(include_feedback=True)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching deliverable: {str(e)}")
        return error_response("Deliverable not found", 404, str(e))

@deliverable_bp.route("/<int:deliverable_id>/download", methods=["GET"])
@jwt_required()
def download_deliverable(deliverable_id):
    """Get secure download URL for deliverable"""
    try:
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        
        # Generate signed URL for secure download (expires in 1 hour)
        download_url = CloudinaryService.generate_download_url(
            deliverable.cloudinary_public_id,
            expires_in=3600  # 1 hour
        )
        
        if not download_url:
            return error_response("Failed to generate download URL", 500)
        
        return jsonify({
            "success": True,
            "download_url": download_url,
            "filename": f"{deliverable.title}_{deliverable.version_number}.{deliverable.file_type}",
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating download URL: {str(e)}")
        return error_response("Failed to generate download URL", 500, str(e))

@deliverable_bp.route("", methods=["POST"])
@jwt_required()
@role_required("freelancer")
def create_deliverable():
    """Upload new deliverable with file"""
    try:
        current_user_id = get_jwt_identity()

        if "file" not in request.files:
            return error_response("No file provided", 400)

        file = request.files["file"]

        if file.filename == "":
            return error_response("No file selected", 400)

        # File size validation
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer

        if file_size > MAX_FILE_SIZE:
            return error_response(f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB", 400)

        project_id = request.form.get("project_id", type=int)
        title = request.form.get("title", "")
        description = request.form.get("description", "")
        change_notes = request.form.get("change_notes", "")

        if not project_id:
            return error_response("Project ID is required", 400)
        
        # Input validation
        try:
            title, description, change_notes = validate_deliverable_data(title, description, change_notes)
        except ValueError as ve:
            return error_response(str(ve), 400)
        
        if not all([
            os.getenv("CLOUDINARY_CLOUD_NAME"),
            os.getenv("CLOUDINARY_API_KEY"),
            os.getenv("CLOUDINARY_API_SECRET")
        ]):
            current_app.logger.error("Cloudinary credentials missing!")
            return error_response("File upload service not configured", 500)

        if not CloudinaryService.allowed_file(file.filename):
            return error_response("File type not allowed", 400)

        file_type = CloudinaryService.get_file_type(file.filename)

        folder = f"reelbrief/project_{project_id}"
        upload_result = CloudinaryService.upload_file(file, folder=folder)

        if not upload_result["success"]:
            current_app.logger.error(f"Cloudinary upload failed: {upload_result.get('error')}")
            return error_response("File upload failed", 500, upload_result.get("error"))

        version_number = Deliverable.get_next_version_number(project_id)

        deliverable = Deliverable(
            project_id=project_id,
            version_number=version_number,
            file_url=upload_result["url"],
            file_type=file_type,
            file_size=upload_result.get("bytes"),
            cloudinary_public_id=upload_result["public_id"],
            thumbnail_url=upload_result.get("thumbnail_url"),
            title=title or f"Version {version_number}",
            description=description,
            change_notes=change_notes,
            uploaded_by=current_user_id,
            status="pending",
        )

        db.session.add(deliverable)
        db.session.commit()

        # Send notification to client
        try:
            project = Project.query.get(project_id)
            if project and project.client_id:
                client = User.query.get(project.client_id)
                freelancer = User.query.get(current_user_id)
                
                if client and client.email:
                    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
                    send_email(
                        recipient=client.email,
                        subject=f"New Deliverable: {deliverable.title}",
                        html_content=f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <h2 style="color: #1E3A8A;">New Deliverable Submitted</h2>
                            <p>Hello {client.first_name},</p>
                            <p><strong>{freelancer.first_name} {freelancer.last_name}</strong> has uploaded a new deliverable:</p>
                            
                            <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                                <h3 style="margin: 0 0 10px 0; color: #1F2937;">{deliverable.title}</h3>
                                <p style="margin: 5px 0;"><strong>Version:</strong> {deliverable.version_number}</p>
                                <p style="margin: 5px 0;"><strong>Project:</strong> {project.title}</p>
                                {f'<p style="margin: 5px 0;"><strong>Changes:</strong> {change_notes}</p>' if change_notes else ''}
                            </div>
                            
                            <a href="{frontend_url}/deliverables/{deliverable.id}" 
                               style="display: inline-block; background-color: #1E3A8A; color: white; 
                                      padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                                Review Deliverable
                            </a>
                        </div>
                        """
                    )
                    current_app.logger.info(f"Notification sent to client: {client.email}")
        except Exception as email_error:
            current_app.logger.error(f"Email notification failed: {str(email_error)}")

        return jsonify({
            "success": True,
            "message": "Deliverable uploaded successfully",
            "deliverable": deliverable.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating deliverable: {str(e)}")
        return error_response("Failed to create deliverable", 500, str(e))

@deliverable_bp.route("/<int:deliverable_id>", methods=["PATCH"])
@jwt_required()
def update_deliverable(deliverable_id):
    """Update deliverable metadata"""
    try:
        current_user_id = get_jwt_identity()
        deliverable = Deliverable.query.get_or_404(deliverable_id)

        if deliverable.uploaded_by != current_user_id:
            return error_response("Unauthorized", 403)

        data = request.get_json()

        # Input validation for updates
        if "title" in data:
            try:
                title, _, _ = validate_deliverable_data(data["title"], "", "")
                deliverable.title = title
            except ValueError as ve:
                return error_response(str(ve), 400)

        if "description" in data:
            try:
                _, description, _ = validate_deliverable_data("", data["description"], "")
                deliverable.description = description
            except ValueError as ve:
                return error_response(str(ve), 400)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Deliverable updated successfully",
            "deliverable": deliverable.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating deliverable: {str(e)}")
        return error_response("Failed to update deliverable", 500, str(e))

@deliverable_bp.route("/<int:deliverable_id>", methods=["DELETE"])
@jwt_required()
def delete_deliverable(deliverable_id):
    """Delete a deliverable"""
    try:
        current_user_id = get_jwt_identity()
        deliverable = Deliverable.query.get_or_404(deliverable_id)

        if deliverable.cloudinary_public_id:
            CloudinaryService.delete_file(
                deliverable.cloudinary_public_id, resource_type="image"
            )

        db.session.delete(deliverable)
        db.session.commit()

        return jsonify({
            "success": True, 
            "message": "Deliverable deleted successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting deliverable: {str(e)}")
        return error_response("Failed to delete deliverable", 500, str(e))

@deliverable_bp.route("/<int:deliverable_id>/versions", methods=["GET"])
@jwt_required()
def get_deliverable_versions(deliverable_id):
    """Get all versions of a deliverable"""
    try:
        deliverable = Deliverable.query.get_or_404(deliverable_id)
        project_id = deliverable.project_id

        versions = (
            Deliverable.query.filter_by(project_id=project_id)
            .order_by(Deliverable.version_number.asc())
            .all()
        )

        return jsonify({
            "success": True,
            "versions": [v.to_dict(include_feedback=False) for v in versions],
            "total_versions": len(versions),
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching versions: {str(e)}")
        return error_response("Failed to fetch versions", 500, str(e))

@deliverable_bp.route("/<int:deliverable_id>/approve", methods=["POST"])
@jwt_required()
@role_required("client", "admin")
def approve_deliverable(deliverable_id):
    """Approve a deliverable and auto-generate portfolio item"""
    try:
        current_user_id = get_jwt_identity()
        deliverable = Deliverable.query.get_or_404(deliverable_id)

        if deliverable.status == "approved":
            return error_response("Deliverable already approved", 400)

        deliverable.approve(reviewed_by_id=current_user_id)
        project = Project.query.get(deliverable.project_id)

        # Portfolio Auto-Generation Logic
        try:
            if (project and 
                project.status == 'completed' and 
                not getattr(project, 'is_sensitive', False) and
                project.freelancer_id):
                
                from app.models.portfolio_item import PortfolioItem
                
                existing_portfolio = PortfolioItem.query.filter_by(
                    project_id=project.id,
                    freelancer_id=project.freelancer_id
                ).first()
                
                if not existing_portfolio:
                    portfolio = create_portfolio_item(project, deliverable)
                    db.session.add(portfolio)
                    current_app.logger.info(f"Auto-generated portfolio item for project {project.id}")
                    
                    # FIXED: Get the project freelancer, not the uploader
                    project_freelancer = User.query.get(project.freelancer_id)
                    if project_freelancer and project_freelancer.email:
                        try:
                            send_email(
                                recipient=project_freelancer.email,
                                subject="Portfolio Item Added!",
                                html_content=f"""
                                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                                    <h2 style="color: #1E3A8A;">Portfolio Item Added</h2>
                                    <p>Hello {project_freelancer.first_name},</p>
                                    <p>Great news! Your project <strong>"{project.title}"</strong> has been automatically added to your portfolio.</p>
                                    <p>Clients can now see this completed work when browsing your profile.</p>
                                    <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                                        <h3 style="margin: 0 0 10px 0; color: #1F2937;">{project.title}</h3>
                                        <p style="margin: 5px 0;"><strong>Status:</strong> Completed & Approved</p>
                                        <p style="margin: 5px 0;"><strong>Deliverable:</strong> {deliverable.title}</p>
                                    </div>
                                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/portfolio" 
                                       style="display: inline-block; background-color: #1E3A8A; color: white; 
                                              padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0;">
                                        View My Portfolio
                                    </a>
                                </div>
                                """
                            )
                        except Exception as portfolio_email_error:
                            current_app.logger.error(f"Portfolio notification email failed: {str(portfolio_email_error)}")
        except Exception as portfolio_error:
            current_app.logger.error(f"Portfolio auto-generation failed: {str(portfolio_error)}")

        # FIXED: Approval notification - use project freelancer, not uploader
        try:
            # Get the project's assigned freelancer
            project_freelancer = User.query.get(project.freelancer_id)
            if project_freelancer and project_freelancer.email:
                send_deliverable_approved_notification(
                    project_freelancer.email,  # FIXED: Use project freelancer email
                    deliverable.title,
                    project.title
                )
                current_app.logger.info(f"Approval notification sent to project freelancer: {project_freelancer.email}")
        except Exception as email_error:
            current_app.logger.error(f"Email notification failed: {str(email_error)}")

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Deliverable approved successfully",
            "deliverable": deliverable.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving deliverable: {str(e)}")
        return error_response("Failed to approve deliverable", 500, str(e))
    
@deliverable_bp.route("/<int:deliverable_id>/request-revision", methods=["POST"])
@jwt_required()
@role_required("client", "admin")
def request_revision(deliverable_id):
    """Request revision on a deliverable"""
    try:
        current_user_id = get_jwt_identity()
        deliverable = Deliverable.query.get_or_404(deliverable_id)

        data = request.get_json()

        if not data or "content" not in data:
            return error_response("Feedback content is required", 400)

        deliverable.request_revision()

        from app.models.feedback import Feedback

        feedback = Feedback(
            deliverable_id=deliverable_id,
            user_id=current_user_id,
            feedback_type="revision",
            content=data["content"],
            priority=data.get("priority", "medium"),
        )

        db.session.add(feedback)
        db.session.commit()

        # FIXED: Get the project's assigned freelancer
        try:
            project = Project.query.get(deliverable.project_id)
            project_freelancer = User.query.get(project.freelancer_id)
            
            if project_freelancer and project_freelancer.email:
                send_deliverable_feedback_notification(
                    project_freelancer.email,  # FIXED: Use project freelancer email
                    deliverable.title,
                    feedback.content
                )
                current_app.logger.info(f"Revision notification sent to project freelancer: {project_freelancer.email}")
        except Exception as email_error:
            current_app.logger.error(f"Email notification failed: {str(email_error)}")

        return jsonify({
            "success": True,
            "message": "Revision requested successfully",
            "deliverable": deliverable.to_dict(),
            "feedback": feedback.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error requesting revision: {str(e)}")
        return error_response("Failed to request revision", 500, str(e))


@deliverable_bp.route("/<int:deliverable_id>/reject", methods=["POST"])
@jwt_required()
@role_required("client", "admin")
def reject_deliverable(deliverable_id):
    """Reject a deliverable"""
    try:
        current_user_id = get_jwt_identity()
        deliverable = Deliverable.query.get_or_404(deliverable_id)

        data = request.get_json() or {}

        deliverable.reject(reviewed_by_id=current_user_id)

        from app.models.feedback import Feedback

        feedback = Feedback(
            deliverable_id=deliverable_id,
            user_id=current_user_id,
            feedback_type="revision",
            content=data.get("reason", "Deliverable rejected"),
            priority="high",
        )

        db.session.add(feedback)
        db.session.commit()

        # FIXED: Get the project's assigned freelancer
        try:
            project = Project.query.get(deliverable.project_id)
            project_freelancer = User.query.get(project.freelancer_id)
            
            if project_freelancer and project_freelancer.email:
                send_deliverable_feedback_notification(
                    project_freelancer.email,  # FIXED: Use project freelancer email
                    deliverable.title,
                    f"REJECTED: {data.get('reason', 'Deliverable rejected')}"
                )
                current_app.logger.info(f"Rejection notification sent to project freelancer: {project_freelancer.email}")
        except Exception as email_error:
            current_app.logger.error(f"Email notification failed: {str(email_error)}")

        return jsonify({
            "success": True,
            "message": "Deliverable rejected",
            "deliverable": deliverable.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error rejecting deliverable: {str(e)}")
        return error_response("Failed to reject deliverable", 500, str(e))

@deliverable_bp.route("/compare", methods=["POST"])
@jwt_required()
def compare_versions():
    """Compare two deliverable versions"""
    try:
        data = request.get_json()

        if not data or "version1_id" not in data or "version2_id" not in data:
            return error_response("Both version IDs are required", 400)

        version1 = Deliverable.query.get_or_404(data["version1_id"])
        version2 = Deliverable.query.get_or_404(data["version2_id"])

        if version1.project_id != version2.project_id:
            return error_response("Versions must be from the same project", 400)

        comparison = {
            "version1": version1.to_dict(include_feedback=True),
            "version2": version2.to_dict(include_feedback=True),
            "differences": {
                "version_diff": version2.version_number - version1.version_number,
                "time_diff_hours": (version2.uploaded_at - version1.uploaded_at).total_seconds() / 3600,
                "size_diff_bytes": version2.file_size - version1.file_size
                if (version1.file_size and version2.file_size)
                else None,
                "status_changed": version1.status != version2.status,
            },
        }

        return jsonify({"success": True, "comparison": comparison}), 200

    except Exception as e:
        current_app.logger.error(f"Error comparing versions: {str(e)}")
        return error_response("Failed to compare versions", 500, str(e))