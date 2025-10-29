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
        cascade='all, delete-orphan'
    )

    # Relationship back to freelancer profiles
    freelancer_profiles = db.relationship(
        'FreelancerProfile', 
        secondary='freelancer_skills',  # Table name as string
        back_populates='skills'
    )

    # Optional relationship for project-skill linkage (if used)
    # project_skills = db.relationship('ProjectSkill', back_populates='skill', cascade='all, delete-orphan')

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
    freelancer_profile = db.relationship(
        'FreelancerProfile', 
        backref=db.backref('skill_associations'))
    skill = db.relationship('Skill')

    # Prevent duplicate (freelancer_id, skill_id)
    __table_args__ = (
        db.UniqueConstraint('freelancer_id', 'skill_id', name='uq_freelancer_skill'),
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
