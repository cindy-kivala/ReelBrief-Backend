"""
Skill Models
Owner: Monica
Description: Skills catalog and freelancer-skill associations with proficiency levels
"""

from app.extensions import db
from datetime import datetime

# TODO: Monica - Implement Skill and FreelancerSkill models
#
# Skill Model:
# - id (Primary Key)
# - name (Unique, e.g., "3D Animation", "Copywriting")
# - category (design, video, writing, etc.)
# - created_at
#
# FreelancerSkill Model (Junction Table):
# - id (Primary Key)
# - freelancer_id (Foreign Key to freelancer_profiles)
# - skill_id (Foreign Key to skills)
# - proficiency (beginner, intermediate, expert)
# - UNIQUE constraint on (freelancer_id, skill_id)
#
# Relationships:
# - Skill has many FreelancerSkill
# - FreelancerSkill belongs to Skill and FreelancerProfile
#
# Example:
# class Skill(db.Model):
#     __tablename__ = 'skills'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), unique=True, nullable=False)
#     # ... rest of fields
#
# class FreelancerSkill(db.Model):
#     __tablename__ = 'freelancer_skills'
#     # ... fields