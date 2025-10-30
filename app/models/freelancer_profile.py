"""
Freelancer Profile Model
Owner: Monica
Description: Extended profile for freelancers with CV, skills, and availability status
"""

from datetime import datetime

from app.extensions import db

# TODO: Monica - Implement FreelancerProfile model
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

# Monica you'll always be the second to do merging. Always confirm with Ryan that he's merged before you merge
"""
Freelancer Profile Model
Owner: Monica
Description:
Extended profile for freelancers including CV, skills, portfolio, and vetting status.
Used by:
- Ryan (signup)
- Monica (vetting)
- Caleb (dashboard stats)
"""

from datetime import datetime
from app.extensions import db
from .skill import FreelancerSkill


class FreelancerProfile(db.Model):
    __tablename__ = 'freelancer_profiles'

    # Primary identifiers
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    #  Basic info
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    bio = db.Column(db.Text)
    portfolio_url = db.Column(db.String(255))
    years_experience = db.Column(db.Integer)
    hourly_rate = db.Column(db.Float)

    #  CV and portfolio
    cv_url = db.Column(db.String(255))
    cv_filename = db.Column(db.String(255))
    cv_uploaded_at = db.Column(db.DateTime)

    # Vetting & status
    application_status = db.Column( db.String(20), default="pending") 
     # pending | approved | rejected
    rejection_reason = db.Column(db.String(255))
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))  # Admin ID
    open_to_work = db.Column(db.Boolean, default=True)

    #  Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column( db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow )

    # Relationships
    user = db.relationship('User', back_populates='freelancer_profile', foreign_keys=[user_id])

    skill_associations = db.relationship(
    "FreelancerSkill", 
    back_populates="freelancer_profile",
    overlaps="freelancer_profiles",
      
)


    skills = db.relationship(
        "Skill",
        secondary="freelancer_skills",
        back_populates="freelancer_profiles",
        overlaps="skill_associations,freelancer_skills,skill"
    )
    # freelancer_skills = db.relationship(
    #     'FreelancerSkill', 
    #     back_populates='freelancer_profile',
    #     cascade='all, delete-orphan'
    # )

    #  Serialization
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "portfolio_url": self.portfolio_url,
            "years_experience": self.years_experience,
            "hourly_rate": self.hourly_rate,
            "cv_url": self.cv_url,
            "cv_filename": self.cv_filename,
            "cv_uploaded_at": self.cv_uploaded_at.isoformat()
            if self.cv_uploaded_at
            else None,
            "application_status": self.application_status,
            "rejection_reason": self.rejection_reason,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "open_to_work": self.open_to_work,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "skills": [skill.name for skill in self.skills],
        }
