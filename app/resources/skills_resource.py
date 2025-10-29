"""
Skill Resource - Public skill list
Owner: Monica
"""

from flask import Blueprint, jsonify
from ..models.skill import Skill

skills_bp = Blueprint("skills", __name__)

@skills_bp.route("/api/skills", methods=["GET"])
def list_skills():
    skills = Skill.query.all()
    return jsonify({
        "skills": [s.to_dict() for s in skills]
    }), 200
# app/schemas/freelancer_schema.py
from marshmallow import Schema, fields

class FreelancerSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    bio = fields.Str()
    cv_url = fields.Str()
    portfolio_url = fields.Str()
    years_experience = fields.Int()
    hourly_rate = fields.Float()
    application_status = fields.Str()
    rejection_reason = fields.Str()
    created_at = fields.DateTime()
