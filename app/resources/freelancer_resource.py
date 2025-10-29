"""
Freelancer Resource - Freelancer Vetting & Management
Owner: Monica
Description:
Handles freelancer CV review, vetting workflow, and availability management.

Connected to:
- FreelancerVetting.jsx (frontend vetting UI)
- AdminDashboard.jsx (Caleb's dashboard stats)
- FreelancerProfile model
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..extensions import db
from ..models.freelancer_profile import FreelancerProfile
from ..models.skill import Skill, FreelancerSkill
import sendgrid
import os
from sendgrid.helpers.mail import Mail

freelancer_bp = Blueprint("freelancers", __name__)

# Helper: SendGrid email sender (safe fallback)
def send_email(to_email, subject, html_content):
    """Utility for sending SendGrid emails (safe if key missing)."""
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key:
        print(" No SENDGRID_API_KEY found — skipping email send.")
        return
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        message = Mail(
            from_email="noreply@freelancer-system.com",
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg.send(message)
        print(f" Email sent to {to_email}")
    except Exception as e:
        print("Email failed:", str(e))


# GET /api/freelancers — List freelancers (admin only)

@freelancer_bp.route("/", methods=["GET"])
@jwt_required()
def list_freelancers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    application_status = request.args.get("application_status")
    open_to_work = request.args.get("open_to_work")
    skills = request.args.getlist("skills")

    query = FreelancerProfile.query

    if application_status:
        query = query.filter(
            FreelancerProfile.application_status == application_status
        )
    if open_to_work:
        query = query.filter(
            FreelancerProfile.open_to_work == (open_to_work.lower() == "true")
        )
    if skills:
        query = query.join(FreelancerProfile.skills).filter(Skill.name.in_(skills))

    paged = query.paginate(page=page, per_page=per_page)
    return (
        jsonify(
            {
                "freelancers": [f.to_dict() for f in paged.items],
                "total": paged.total,
                "page": paged.page,
            }
        ),200,)


#  GET /api/freelancers/<id> — View one freelancer

@freelancer_bp.route("/<int:freelancer_id>", methods=["GET"])
@jwt_required()
def get_freelancer(freelancer_id):
    freelancer = FreelancerProfile.query.get_or_404(freelancer_id)
    return jsonify(freelancer.to_dict()), 200


# GET /api/freelancers/pending — List pending freelancers

@freelancer_bp.route("/pending", methods=["GET"])
@jwt_required()
def get_pending_freelancers():
    freelancers = FreelancerProfile.query.filter_by(application_status="pending").all()
    return (
        jsonify(
            {
                "success": True,
                "freelancers": [f.to_dict() for f in freelancers],
            }
        ),
        200,)


# PATCH /api/freelancers/<id>/approve — Approve freelancer

@freelancer_bp.route("/<int:freelancer_id>/approve", methods=["PATCH"])
@jwt_required()
def approve_freelancer(freelancer_id):
    freelancer = FreelancerProfile.query.get_or_404(freelancer_id)
    freelancer.application_status = "approved"
    freelancer.approved_at = db.func.now()
    freelancer.approved_by = get_jwt_identity()

    db.session.commit()

    send_email(
        freelancer.email,
        "Freelancer Application Approved",
        f"""
        <p>Hi {freelancer.name},</p>
        <p>Congratulations! Your application has been <b>approved</b>.</p>
        <p>You can now apply for available projects on our platform.</p>
        """,)

    return (
        jsonify(
            {
                "success": True,
                "message": "Freelancer approved successfully",
                "freelancer": freelancer.to_dict(),
            }
        ),
        200,)


# PATCH /api/freelancers/<id>/reject — Reject freelancer

@freelancer_bp.route("/<int:freelancer_id>/reject", methods=["PATCH"])
@jwt_required()
def reject_freelancer(freelancer_id):
    data = request.get_json() or {}
    reason = data.get("rejection_reason", "No reason provided")

    freelancer = FreelancerProfile.query.get_or_404(freelancer_id)
    freelancer.application_status = "rejected"
    freelancer.rejection_reason = reason
    db.session.commit()

    send_email(
        freelancer.email,
        "Freelancer Application Rejected",
        f"""
        <p>Hi {freelancer.name},</p>
        <p>Unfortunately, your application has been <b>rejected</b>.</p>
        <p><b>Reason:</b> {reason}</p>
        <p>You can update your profile and reapply later.</p>
        """,
    )

    return (
        jsonify(
            {
                "success": True,
                "message": "Freelancer rejected successfully",
                "freelancer": freelancer.to_dict(),
            }
        ),
        200,
    )


# PATCH /api/freelancers/<id>/toggle-availability

@freelancer_bp.route(
    "/<int:freelancer_id>/toggle-availability", methods=["PATCH"]
)
@jwt_required()
def toggle_availability(freelancer_id):
    user_id = get_jwt_identity()
    freelancer = FreelancerProfile.query.get_or_404(freelancer_id)

    if freelancer.user_id != user_id:
        return jsonify({"error": "You can only update your own availability"}), 403

    freelancer.open_to_work = not freelancer.open_to_work
    db.session.commit()

    return jsonify({"message": "Availability updated", "freelancer": freelancer.to_dict()}), 200


# POST /api/freelancers/<id>/skills — Add or update skill

@freelancer_bp.route("/<int:freelancer_id>/skills", methods=["POST"])
@jwt_required()
def add_skill(freelancer_id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    skill_id = data.get("skill_id")
    proficiency = data.get("proficiency", "intermediate")

    freelancer = FreelancerProfile.query.get_or_404(freelancer_id)
    if freelancer.user_id != user_id:
        return jsonify({"error": "You can only modify your own skills"}), 403

    skill = Skill.query.get_or_404(skill_id)

    existing = FreelancerSkill.query.filter_by(
        freelancer_id=freelancer.id, skill_id=skill.id).first()
    if existing:
        existing.proficiency = proficiency
    else:
        link = FreelancerSkill(
            freelancer=freelancer, skill=skill, proficiency=proficiency)
        db.session.add(link)

    db.session.commit()
    return jsonify({"message": "Skill updated successfully", "skills": [s.to_dict() for s in freelancer.skills]}), 200


#  GET /api/freelancers/search — Find freelancers by skills or experience

@freelancer_bp.route("/search", methods=["GET"])
@jwt_required()
def search_freelancers():
    skills = request.args.getlist("skills")
    open_to_work = request.args.get("open_to_work", "true").lower() == "true"
    min_experience = request.args.get("min_experience")

    query = FreelancerProfile.query.filter(
        FreelancerProfile.open_to_work == open_to_work)
    if min_experience:
        query = query.filter(FreelancerProfile.years_experience >= int(min_experience))
    if skills:
        query = query.join(FreelancerProfile.skills).filter(Skill.name.in_(skills))

    freelancers = query.distinct().all()
    return jsonify({"results": [f.to_dict() for f in freelancers], "count": len(freelancers)}), 200


# GET /api/freelancers/stats — Dashboard counts (for Caleb)

@freelancer_bp.route("/stats", methods=["GET"])
@jwt_required()
def freelancer_stats():
    pending = FreelancerProfile.query.filter_by(application_status="pending").count()
    approved = FreelancerProfile.query.filter_by(application_status="approved").count()
    rejected = FreelancerProfile.query.filter_by(application_status="rejected").count()

    return jsonify({"success": True, "stats": {"pending": pending, "approved": approved, "rejected": rejected}}), 200
