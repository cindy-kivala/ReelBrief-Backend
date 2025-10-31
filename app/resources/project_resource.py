"""
Project Resource - Project Management Endpoints
Owner: Monica
Description: CRUD operations for projects + assignment logic
"""


from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.project import Project, ProjectSkill
from ..models.freelancer_profile import FreelancerProfile
from ..models.skill import Skill
from ..extensions import db
from ..services.project_service import ProjectService
from app.models.user import User
import sendgrid
import os
from sendgrid.helpers.mail import Mail

project_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


# Helper: send email (used on assignment)

def send_email(to_email, subject, html):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    msg = Mail(
        from_email="noreply@freelancer-system.com",
        to_emails=to_email,
        subject=subject,
        html_content=html,
    )
    try:
        sg.send(msg)
    except Exception as e:
        print("Email error:", str(e))


@project_bp.route("", methods=["GET"])
@jwt_required()
def get_projects():
    try:
        print("=== GET /api/projects called ===")  # Debug line
        
        # Get current user info
        current_user = get_jwt_identity()
        print(f"Current user: {current_user}")  # Debug line
        
        user_id = current_user
        if isinstance(current_user, dict):
            user_id = current_user.get('id')
        
        # Get user from database
        user = User.query.get(user_id)
        print(f"User found: {user}")  # Debug line
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        role = user.role
        print(f"User role: {role}")  # Debug line
        
        # Simple query without pagination first
        query = Project.query
        print(f"Base query: {query}")  # Debug line
        
        # Apply role-based filtering
        if role == "client":
            query = query.filter_by(client_id=user_id)
        elif role == "freelancer":
            query = query.filter_by(freelancer_id=user_id)
        
        projects = query.order_by(Project.created_at.desc()).limit(10).all()
        print(f"Projects found: {len(projects)}")  # Debug line
        
        projects_data = []
        for project in projects:
            project_dict = project.to_dict()
            projects_data.append(project_dict)
        
        return jsonify({
            'projects': projects_data,
            'total': len(projects_data),
            'pages': 1,
            'current_page': 1
        }), 200
        
    except Exception as e:
        print(f"=== ERROR in get_projects: {str(e)} ===")  # Debug line
        import traceback
        traceback.print_exc()  # This will print the full traceback
        return jsonify({'error': str(e)}), 500

# GET /api/projects/<id>
@project_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify(project.to_dict()), 200


# POST /api/projects
@project_bp.route("/", methods=["POST"])
@jwt_required()
def create_project():
    data = request.get_json() or {}
    user_id = get_jwt_identity()

    project = Project(
        title=data.get("title"),
        description=data.get("description"),
        client_id=user_id,
        budget=data.get("budget"),
        deadline=data.get("deadline"),
        project_type=data.get("project_type"),
        is_sensitive=data.get("is_sensitive", False),
        status="submitted",
    )

    # attach required skills
    required_skills = data.get("required_skills", [])
    for s in required_skills:
        skill = Skill.query.get_or_404(s.get("skill_id"))
        link = ProjectSkill(skill=skill, required_proficiency=s.get("required_proficiency", "intermediate"))
        project.required_skills.append(link)

    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


# PATCH /api/projects/<id>
@project_bp.route("/<int:project_id>", methods=["PATCH"])
@jwt_required()
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json() or {}

    # Update attributes
    for key, value in data.items():
        if key in ["title", "description", "budget", "deadline", "project_type", "priority", "is_sensitive"]:
            setattr(project, key, value)

    # update required skills
    if "required_skills" in data:
        project.required_skills.clear()
        for s in data["required_skills"]:
            skill = Skill.query.get_or_404(s.get("skill_id"))
            ps = ProjectSkill(skill=skill, required_proficiency=s.get("required_proficiency", "intermediate"))
            project.required_skills.append(ps)

    db.session.commit()
    return jsonify(project.to_dict()), 200


# DELETE /api/projects/<id>
@project_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = "cancelled"
    project.cancelled_at = db.func.now()
    project.cancellation_reason = request.json.get("reason", "Cancelled by admin")
    db.session.commit()
    return jsonify({"message": "Project cancelled"}), 200


# GET /api/projects/available-freelancers
@project_bp.route("/available-freelancers", methods=["GET"])
@jwt_required()
def get_available_freelancers():
    """Get list of available freelancers with their user IDs"""
    try:
        available_freelancers = FreelancerProfile.query.filter_by(
            open_to_work=True, 
            application_status="approved"
        ).all()
        
        freelancers_data = []
        for profile in available_freelancers:
            user = User.query.get(profile.user_id)
            if user:
                freelancers_data.append({
                    "user_id": user.id,  # This is the ID to use for assignment
                    "freelancer_profile_id": profile.id,
                    "name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "skills": [skill.name for skill in profile.skills],
                    "years_experience": profile.years_experience,
                    "hourly_rate": profile.hourly_rate
                })
        
        return jsonify({
            "success": True,
            "freelancers": freelancers_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# POST /api/projects/<id>/assign-freelancer
@project_bp.route("/<int:project_id>/assign-freelancer", methods=["POST"])
@jwt_required()
def assign_freelancer(project_id):
    data = request.get_json() or {}
    freelancer_user_id = data.get("freelancer_id")  # This should be the USER ID

    project = Project.query.get_or_404(project_id)
    
    # Check if user exists
    freelancer_user = User.query.get(freelancer_user_id)
    if not freelancer_user:
        return jsonify({"error": f"User with ID {freelancer_user_id} not found"}), 404
    
    # Check if user has a freelancer profile
    freelancer_profile = FreelancerProfile.query.filter_by(user_id=freelancer_user_id).first()
    if not freelancer_profile:
        return jsonify({"error": "User is not registered as a freelancer"}), 400

    if not freelancer_profile.open_to_work:
        return jsonify({"error": "Freelancer not open to work"}), 400

    # Assign using the USER ID (this should match the foreign key constraint)
    project.freelancer_id = freelancer_user.id  # Use the user ID
    project.status = "matched"
    project.matched_at = db.func.now()
    freelancer_profile.open_to_work = False

    db.session.commit()

    send_email(
        freelancer_user.email,
        "New Project Assigned",
        f"<p>Hi {freelancer_user.first_name},</p><p>You've been assigned to project <b>{project.title}</b>.</p>",
    )

    return jsonify({
        "message": "Freelancer assigned successfully", 
        "project": project.to_dict()
    }), 200


# POST /api/projects/<id>/complete
@project_bp.route("/<int:project_id>/complete", methods=["POST"])
@jwt_required()
def complete_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = "completed"
    project.completed_at = db.func.now()
    db.session.commit()

    # trigger portfolio creation if not sensitive (placeholder)
    if not project.is_sensitive:
        print(f"Auto-creating portfolio item for project {project.title}")

    return jsonify({"message": "Project marked as completed"}), 200


@project_bp.route("/<int:project_id>/suggest-freelancers", methods=["GET"])
@jwt_required()
def suggest_freelancers(project_id):
    project = Project.query.get_or_404(project_id)
    matches = ProjectService.match_freelancers_to_project(project)
    return jsonify({"matches": matches}), 200