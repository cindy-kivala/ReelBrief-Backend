"""
Freelancer Profile Model
Owner: Ryan
Description: Extended profile for freelancers with CV, skills, and availability status.
"""

from datetime import datetime

from app.extensions import db


# Ryan you'll always be the second to do merging. Always confirm with Ryan that he's merged before you merge
from ..extensions import db
from datetime import datetime
from .skill import FreelancerSkill

class FreelancerProfile(db.Model):
    __tablename__ = 'freelancer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    bio = db.Column(db.Text)
    cv_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # many-to-many → freelancer ↔ skills
    skills = db.relationship('Skill', secondary=FreelancerSkill, backref='freelancers')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "cv_url": self.cv_url,
            "is_available": self.is_available,
            "approved": self.approved,
            "skills": [skill.name for skill in self.skills]
        }
