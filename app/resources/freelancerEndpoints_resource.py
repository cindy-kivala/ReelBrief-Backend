# app/routes/freelancer_routes.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.freelancer import Freelancer
from app.schemas.freelancer_schema import FreelancerSchema

freelancer_bp = Blueprint("freelancer", __name__, url_prefix="/api/freelancers")
schema = FreelancerSchema()
schema_many = FreelancerSchema(many=True)

# GET pending freelancers (for admin)
@freelancer_bp.route("/pending", methods=["GET"])
def get_pending_freelancers():
    freelancers = Freelancer.query.filter_by(application_status="pending").all()
    return jsonify({"success": True, "freelancers": schema_many.dump(freelancers)})

# GET all freelancers (for clients) 
@freelancer_bp.route("/", methods=["GET"])
def get_all_freelancers():
    freelancers = Freelancer.query.all()
    return jsonify({"success": True, "freelancers": schema_many.dump(freelancers)})

#  POST: submit vetting documents 
@freelancer_bp.route("/submit", methods=["POST"])
def submit_freelancer():
    data = request.form
    name = data.get("name")
    email = data.get("email")
    bio = data.get("bio")
    years_experience = data.get("years_experience", 0)
    hourly_rate = data.get("hourly_rate", 0.0)

    cv_file = request.files.get("cv")
    portfolio_file = request.files.get("portfolio")

    cv_url = f"/uploads/{cv_file.filename}" if cv_file else None
    portfolio_url = f"/uploads/{portfolio_file.filename}" if portfolio_file else None

    if cv_file:
        cv_file.save(f"uploads/{cv_file.filename}")
    if portfolio_file:
        portfolio_file.save(f"uploads/{portfolio_file.filename}")

    freelancer = Freelancer(
        name=name,
        email=email,
        bio=bio,
        years_experience=years_experience,
        hourly_rate=hourly_rate,
        cv_url=cv_url,
        portfolio_url=portfolio_url
    )
    db.session.add(freelancer)
    db.session.commit()

    return jsonify({"success": True, "freelancer": schema.dump(freelancer)})

#  PATCH approve freelancer 
@freelancer_bp.route("/<int:id>/approve", methods=["PATCH"])
def approve_freelancer(id):
    freelancer = Freelancer.query.get_or_404(id)
    freelancer.application_status = "approved"
    db.session.commit()
    return jsonify({"success": True, "freelancer": schema.dump(freelancer)})

# PATCH reject freelancer
@freelancer_bp.route("/<int:id>/reject", methods=["PATCH"])
def reject_freelancer(id):
    freelancer = Freelancer.query.get_or_404(id)
    reason = request.json.get("reason")
    freelancer.application_status = "rejected"
    freelancer.rejection_reason = reason
    db.session.commit()
    return jsonify({"success": True, "freelancer": schema.dump(freelancer)})
