"""
Project Models
Owner: Monica
Description: Project management with status tracking, deliverables, and skill requirements.
"""

from datetime import datetime
from ..extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    # -------------------- Primary Key --------------------
    id = db.Column(db.Integer, primary_key=True)

    # -------------------- Core Info --------------------
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # -------------------- Foreign Keys (linked users) --------------------
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # -------------------- Project Details --------------------
    status = db.Column(db.String(50), default="submitted")  # submitted, in_progress, completed, etc.
    budget = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    is_sensitive = db.Column(db.Boolean, default=False)
    payment_status = db.Column(
        db.String(50), default="unpaid"
    )  # unpaid, in_escrow, released, refunded
    project_type = db.Column(db.String(100))
    priority = db.Column(db.String(50), default="normal")

    # -------------------- Time Tracking --------------------
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    matched_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)

    # -------------------- Relationships --------------------
    # Each project can have multiple required skills
    required_skills = db.relationship(
        "ProjectSkill",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # ✅ Added: Each project can have multiple deliverables (one-to-many)
    deliverables = db.relationship(
        "Deliverable",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # -------------------- Methods --------------------
    def to_dict(self):
        """Convert project instance into JSON-serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "admin_id": self.admin_id,
            "status": self.status,
            "budget": self.budget,
            "deadline": self.deadline.strftime("%Y-%m-%d") if self.deadline else None,
            "is_sensitive": self.is_sensitive,
            "payment_status": self.payment_status,
            "project_type": self.project_type,
            "priority": self.priority,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.created_at
            else None,
            "matched_at": self.matched_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.matched_at
            else None,
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.started_at
            else None,
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.completed_at
            else None,
            "cancelled_at": self.cancelled_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.cancelled_at
            else None,
            "cancellation_reason": self.cancellation_reason,
            "required_skills": [rs.to_dict() for rs in self.required_skills],
            # ✅ Include basic deliverable info
            "deliverables": [
                {
                    "id": d.id,
                    "title": d.title,
                    "status": d.status,
                    "version_number": d.version_number,
                }
                for d in self.deliverables
            ],
        }


# -------------------------------------------------------------------
# ProjectSkill Model
# -------------------------------------------------------------------
class ProjectSkill(db.Model):
    __tablename__ = "project_skills"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    # 🔧 Temporarily disable the skill relationship until Skill model is active
    # skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    skill_id = db.Column(db.Integer, nullable=True)

    required_proficiency = db.Column(db.String(50), default="intermediate")

    # Relationship to parent project
    project = db.relationship("Project", back_populates="required_skills")
    # skill = db.relationship("Skill")  # 🔧 Disabled until Skill model is active

    __table_args__ = (
        db.UniqueConstraint("project_id", "skill_id", name="uq_project_skill"),
    )

    def to_dict(self):
        """Serialize ProjectSkill to dict."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "skill_id": self.skill_id,
            "required_proficiency": self.required_proficiency,
        }
