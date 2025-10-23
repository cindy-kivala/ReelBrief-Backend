"""
Project Models
Owner: Monica
Description: Project management with status tracking and skill requirements
"""

from datetime import datetime

from app.extensions import db

# TODO: Monica - Implement Project and ProjectSkill models
#
class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deliverables = db.relationship('Deliverable', backref='project', lazy=True)
    # feedback = db.relationship('Feedback', backref='project', lazy=True)

    @property
    def all_feedback(self):
        feedback_list = []
        for deliverable in self.deliverables:
            feedback_list.extend(deliverable.feedback)
        return feedback_list
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
