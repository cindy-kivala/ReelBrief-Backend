"""
Project Models
Owner: Monica
Description: Project management with status tracking and skill requirements
"""

from datetime import datetime

from app.extensions import db

# TODO: Monica - Implement Project and ProjectSkill models
#
# Project Model:
# - id (Primary Key)
# - title, description
# - client_id (Foreign Key to users)
# - freelancer_id (Foreign Key to users, nullable)
# - admin_id (Foreign Key to users)
# - status (submitted, matching, matched, in_progress, pending_review, etc.)
# - budget, deadline
# - is_sensitive (Boolean for confidential projects)
# - payment_status (unpaid, in_escrow, released, refunded)
# - project_type, priority
# - created_at, matched_at, started_at, completed_at, cancelled_at
# - cancellation_reason
#
# ProjectSkill Model (Junction Table):
# - id (Primary Key)
# - project_id (Foreign Key to projects)
# - skill_id (Foreign Key to skills)
# - required_proficiency (beginner, intermediate, expert)
# - UNIQUE constraint on (project_id, skill_id)
#
# Relationships:
# - Project belongs to client (User)
# - Project belongs to freelancer (User)
# - Project has many required_skills (ProjectSkill)
# - Project has many deliverables
# - Project has one escrow_transaction
# - Project has one portfolio_item
#
# Methods:
# - to_dict()
#
# Example:
# class Project(db.Model):
#     __tablename__ = 'projects'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields
