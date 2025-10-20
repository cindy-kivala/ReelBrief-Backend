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
