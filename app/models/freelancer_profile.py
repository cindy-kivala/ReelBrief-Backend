"""
Freelancer Profile Model
Owner: Ryan
Description: Extended profile for freelancers with CV, skills, and availability status
"""

from datetime import datetime

from app.extensions import db

# TODO: Ryan - Implement FreelancerProfile model
#
# Required fields:
# - id (Primary Key)
# - user_id (Foreign Key to users, Unique)
# - bio
# - cv_url, cv_filename, cv_uploaded_at
# - application_status (pending, approved, rejected)
# - rejection_reason
# - open_to_work (Boolean, default True)
# - hourly_rate
# - portfolio_url
# - years_experience
# - approved_at, approved_by
# - created_at
#
# Relationships:
# - user (one-to-one back reference)
# - skills (one-to-many to FreelancerSkill)
# - portfolio_items (one-to-many)
#
# Methods:
# - to_dict()
#
# Example:
# class FreelancerProfile(db.Model):
#     __tablename__ = 'freelancer_profiles'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields

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
