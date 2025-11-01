"""
Skill Models
Owner: Monica
Description: Skills catalog and freelancer-skill associations with proficiency levels
"""

from datetime import datetime
from ..extensions import db

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one skill -> many FreelancerSkill
    freelancer_skills = db.relationship(
        'FreelancerSkill',
        back_populates='skill',
        cascade='all, delete-orphan',
        overlaps="freelancer_profiles"
    )

    # Many-to-many relationship with FreelancerProfile
    freelancer_profiles = db.relationship(
        "FreelancerProfile",
        secondary="freelancer_skills",
        back_populates="skills",
        overlaps="freelancer_skills"
    )

    def __repr__(self):
        return f"<Skill {self.name}>"

    def to_dict(self):
        """Return a serialized version of the Skill."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }

class FreelancerSkill(db.Model):
    __tablename__ = 'freelancer_skills'

    id = db.Column(db.Integer, primary_key=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('freelancer_profiles.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)

    proficiency = db.Column(
        db.String(50),
        default='intermediate'
    )  # beginner, intermediate, expert

    # Relationships
    skill = db.relationship(
        "Skill",
        back_populates="freelancer_skills",
        overlaps="freelancer_profiles,skills"
    )

    freelancer_profile = db.relationship(
        'FreelancerProfile',
        back_populates="skill_associations",
        overlaps="freelancer_profiles,skills"
    )

    def __repr__(self):
        return f"<FreelancerSkill freelancer={self.freelancer_id}, skill={self.skill_id}, level={self.proficiency}>"

    def to_dict(self):
        """Return a JSON-serializable representation."""
        return {
            "id": self.id,
            "freelancer_id": self.freelancer_id,
            "skill_id": self.skill_id,
            "skill_name": self.skill.name if self.skill else None,
            "proficiency": self.proficiency
        }
