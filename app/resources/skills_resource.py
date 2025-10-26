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
