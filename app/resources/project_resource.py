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
import sendgrid
import os
from sendgrid.helpers.mail import Mail

project_bp = Blueprint("projects", __name__)


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



# GET /api/projects

@project_bp.route("/", methods=["GET"])
@jwt_required()
def get_projects():
    user_id = get_jwt_identity()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    status = request.args.get("status")
    client_id = request.args.get("client_id")
    freelancer_id = request.args.get("freelancer_id")

    # role filtering (in real app, determine role via JWT claims)
    query = Project.query
    if client_id:
        query = query.filter(Project.client_id == int(client_id))
    if freelancer_id:
        query = query.filter(Project.freelancer_id == int(freelancer_id))
    if status:
        query = query.filter(Project.status == status)

    projects = query.paginate(page=page, per_page=per_page)
    return jsonify({
        "projects": [p.to_dict() for p in projects.items],
        "total": projects.total,
        "page": projects.page
    }), 200



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



# POST /api/projects/<id>/assign-freelancer

@project_bp.route("/<int:project_id>/assign-freelancer", methods=["POST"])
@jwt_required()
def assign_freelancer(project_id):
    data = request.get_json() or {}
    freelancer_id = data.get("freelancer_id")

    project = Project.query.get_or_404(project_id)
    freelancer = FreelancerProfile.query.get_or_404(freelancer_id)

    if not freelancer.open_to_work:
        return jsonify({"error": "Freelancer not open to work"}), 400

    project.freelancer_id = freelancer.id
    project.status = "matched"
    project.matched_at = db.func.now()
    freelancer.open_to_work = False

    db.session.commit()

    send_email(
        freelancer.email,
        "New Project Assigned",
        f"<p>Hi {freelancer.name},</p><p>You’ve been assigned to project <b>{project.title}</b>.</p>",
    )

    return jsonify({"message": "Freelancer assigned successfully", "project": project.to_dict()}), 200



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

