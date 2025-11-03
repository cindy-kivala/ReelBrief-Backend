"""
Project Approval Routes - Admin-Mediated Workflow
Owner: Cindy
Description: API endpoints for project approval, shortlisting, and assignment
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.project import Project
from app.services.project_approval_service import ProjectApprovalService
from app.utils.decorators import role_required
from app.extensions import db

project_approval_bp = Blueprint("project_approval", __name__, url_prefix="/api/projects")


@project_approval_bp.route("/<int:project_id>/check-feasibility", methods=["GET"])
@jwt_required()
@role_required("admin")
def check_project_feasibility(project_id):
    """
    Check if project is feasible (admin only)
    GET /api/projects/:id/check-feasibility
    """
    try:
        result = ProjectApprovalService.check_project_feasibility(project_id)
        
        return jsonify({
            "success": True,
            "is_feasible": result['is_feasible'],
            "matching_freelancers": [
                {
                    'freelancer': item['freelancer'].to_dict(),
                    'match_score': item['match_score'],
                    'matching_skills': item['matching_skills']
                }
                for item in result.get('matching_freelancers', [])
            ],
            "reasons": result.get('reasons', [])
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@project_approval_bp.route("/<int:project_id>/approve", methods=["POST"])
@jwt_required()
@role_required("admin")
def approve_project(project_id):
    """
    Approve project and generate shortlist (admin only)
    POST /api/projects/:id/approve
    """
    try:
        current_user_id = get_jwt_identity()
        
        result = ProjectApprovalService.approve_project(project_id, current_user_id)
        
        return jsonify({
            "success": True,
            "message": "Project approved and shortlist sent to client",
            "project": result['project'],
            "shortlisted_freelancers": result['shortlisted_freelancers'],
            "email_sent": result['email_sent']
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to approve project: {str(e)}"
        }), 500


@project_approval_bp.route("/<int:project_id>/reject-feasibility", methods=["POST"])
@jwt_required()
@role_required("admin")
def reject_project_feasibility(project_id):
    """
    Reject project as not feasible (admin only)
    POST /api/projects/:id/reject-feasibility
    Body: { "reason": "Not enough qualified freelancers available" }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        reason = data.get('reason')
        if not reason:
            return jsonify({
                "success": False,
                "error": "Rejection reason is required"
            }), 400
        
        result = ProjectApprovalService.reject_project_feasibility(
            project_id, 
            current_user_id, 
            reason
        )
        
        return jsonify({
            "success": True,
            "message": "Project marked as not feasible and client notified",
            "project": result['project'],
            "email_sent": result['email_sent']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to reject project: {str(e)}"
        }), 500


@project_approval_bp.route("/<int:project_id>/shortlist", methods=["GET"])
@jwt_required()
@role_required("client", "admin")
def get_project_shortlist(project_id):
    """
    Get shortlisted freelancers for a project (client & admin)
    GET /api/projects/:id/shortlist
    """
    try:
        current_user_id = get_jwt_identity()
        project = Project.query.get_or_404(project_id)
        
        # Authorization: Only project client or admin can view shortlist
        user = User.query.get(current_user_id)
        if user.role != 'admin' and project.client_id != current_user_id:
            return jsonify({
                "success": False,
                "error": "You are not authorized to view this shortlist"
            }), 403
        
        shortlist = ProjectApprovalService.get_project_shortlist(project_id)
        
        return jsonify({
            "success": True,
            "project_id": project_id,
            "project_title": project.title,
            "shortlisted_freelancers": shortlist
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@project_approval_bp.route("/<int:project_id>/assign-freelancer", methods=["POST"])
@jwt_required()
@role_required("client", "admin")
def assign_freelancer_to_project(project_id):
    """
    Assign freelancer to project (client or admin)
    POST /api/projects/:id/assign-freelancer
    Body: { "freelancer_id": 5 }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        freelancer_id = data.get('freelancer_id')
        if not freelancer_id:
            return jsonify({
                "success": False,
                "error": "freelancer_id is required"
            }), 400
        
        # Authorization: Only project client or admin can assign
        project = Project.query.get_or_404(project_id)
        user = User.query.get(current_user_id)
        
        if user.role != 'admin' and project.client_id != current_user_id:
            return jsonify({
                "success": False,
                "error": "You are not authorized to assign freelancers to this project"
            }), 403
        
        result = ProjectApprovalService.assign_freelancer_to_project(
            project_id,
            freelancer_id,
            current_user_id
        )
        
        return jsonify({
            "success": True,
            "message": "Freelancer assigned successfully. All parties have been notified.",
            "project": result['project'],
            "freelancer": result['freelancer'],
            "assigned_by": result['assigned_by']
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        # Check if it's a 404 error from get_or_404
        if "404" in str(e):
            return jsonify({
                "success": False,
                "error": "Freelancer not found"
            }), 400
        return jsonify({
            "success": False,
            "error": f"Failed to assign freelancer: {str(e)}"
        }), 500
    


@project_approval_bp.route("/<int:project_id>/request-admin-assignment", methods=["POST"])
@jwt_required()
@role_required("client")
def request_admin_assignment(project_id):
    """
    Client requests admin to assign the best freelancer
    POST /api/projects/:id/request-admin-assignment
    """
    try:
        current_user_id = get_jwt_identity()
        project = Project.query.get_or_404(project_id)
        
        # Authorization: Only project client
        if project.client_id != current_user_id:
            return jsonify({
                "success": False,
                "error": "You are not authorized to make this request"
            }), 403
        
        if project.status != 'approved':
            return jsonify({
                "success": False,
                "error": "Project must be approved before requesting assignment"
            }), 400
        
        # Update project to indicate admin assignment requested
        project.assignment_requested = True
        
        # Notify all admins
        from app.models.notification import Notification
        admin_users = User.query.filter_by(role='admin').all()
        client = User.query.get(current_user_id)
        
        for admin in admin_users:
            notification = Notification(
                user_id=admin.id,
                type='assignment_request',
                title=f'Assignment Request: {project.title}',
                message=f'{client.first_name} {client.last_name} has requested admin assignment for project "{project.title}"',
                related_project_id=project.id
            )
            db.session.add(notification)
            
            # Send email to admin
            from app.services.email_service import send_email
            import os
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            
            send_email(
                recipient=admin.email,
                subject=f"Assignment Request: {project.title}",
                html_content=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #1E3A8A;">Freelancer Assignment Request</h2>
                    <p>Hello {admin.first_name},</p>
                    <p><strong>{client.first_name} {client.last_name}</strong> has requested admin assistance with freelancer assignment for:</p>
                    
                    <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #1F2937;">{project.title}</h3>
                        <p style="margin: 5px 0;"><strong>Budget:</strong> ${project.budget}</p>
                        <p style="margin: 5px 0;"><strong>Deadline:</strong> {project.deadline.strftime('%B %d, %Y') if project.deadline else 'Not specified'}</p>
                    </div>
                    
                    <p style="margin: 20px 0;">
                        <a href="{frontend_url}/projects/{project.id}" 
                           style="display: inline-block; background-color: #1E3A8A; color: white; 
                                  padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                            Review & Assign Freelancer
                        </a>
                    </p>
                </div>
                """
            )
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Admin has been notified of your assignment request",
            "project": project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to request admin assignment: {str(e)}"
        }), 500


@project_approval_bp.route("/pending-approval", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_pending_approval_projects():
    """
    Get all projects pending admin approval
    GET /api/projects/pending-approval
    """
    try:
        projects = Project.query.filter_by(status='submitted').order_by(Project.created_at.desc()).all()
        
        # Add feasibility check for each project
        projects_with_feasibility = []
        for project in projects:
            feasibility = ProjectApprovalService.check_project_feasibility(project.id)
            project_dict = project.to_dict()
            project_dict['is_feasible'] = feasibility['is_feasible']
            project_dict['matching_freelancers_count'] = len(feasibility.get('matching_freelancers', []))
            projects_with_feasibility.append(project_dict)
        
        return jsonify({
            "success": True,
            "projects": projects_with_feasibility,
            "total": len(projects_with_feasibility)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@project_approval_bp.route("/pending-assignment", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_pending_assignment_projects():
    """
    Get all approved projects pending freelancer assignment
    GET /api/projects/pending-assignment
    """
    try:
        projects = Project.query.filter(
            Project.status == 'approved',
            Project.freelancer_id == None
        ).order_by(Project.approved_at.desc()).all()
        
        return jsonify({
            "success": True,
            "projects": [p.to_dict() for p in projects],
            "total": len(projects)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500