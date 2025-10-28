"""
Project Models
Owner: Monica
Description: Project management with status tracking and skill requirements
"""

from datetime import datetime

from app.extensions import db

# TODO: Monica - Implement Project and ProjectSkill models
"""
Minimal Project Model for Testing
This is a temporary stub until the full Project model is merged
"""

from datetime import datetime

from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Basic fields
    title = db.Column(db.String(255), nullable=False, default="Test Project")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to deliverables (back_populates must match Deliverable.project)
    deliverables = db.relationship("Deliverable", back_populates="project", lazy=True)

    def __repr__(self):
        return f"<Project {self.id}: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


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
