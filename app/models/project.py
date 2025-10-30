# app/models/project.py
"""
Project Models
Owner: Monica
Description: Project management with status tracking, deliverables, and skill requirements.
"""

from datetime import datetime
from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    # -------------------- Primary Key --------------------
    id = db.Column(db.Integer, primary_key=True)

    # -------------------- Core Info --------------------
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # -------------------- Foreign Keys (linked users) --------------------
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # -------------------- Project Details --------------------
    status = db.Column(
        db.String(50),
        default="submitted",  # submitted, in_progress, pending_review, completed, etc.
    )
    budget = db.Column(db.Numeric(10, 2), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    is_sensitive = db.Column(db.Boolean, default=False)
    payment_status = db.Column(
        db.String(50), default="unpaid"  # unpaid, in_escrow, released, refunded
    )
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
    # Required skills (one-to-many)
    required_skills = db.relationship(
        "ProjectSkill",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Users
    client = db.relationship("User", foreign_keys=[client_id], backref="client_projects")
    freelancer = db.relationship(
        "User", foreign_keys=[freelancer_id], backref="freelancer_projects"
    )
    admin = db.relationship("User", foreign_keys=[admin_id])

    # Deliverables (one-to-many)
    deliverables = db.relationship(
        "Deliverable",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy=True,
    )

    # Escrow (one-to-one) — use back_populates to avoid name collision
    escrow_transaction = db.relationship(
        "EscrowTransaction",
        back_populates="project",
        uselist=False,
        lazy=True,
    )

    # -------------------- Methods --------------------
    def _calculate_progress(self) -> int:
        if not self.deliverables:
            return 0
        total = len(self.deliverables)
        completed = len([d for d in self.deliverables if d.status == "approved"])
        return int((completed / total) * 100) if total > 0 else 0

    def to_dict(self) -> dict:
        """Convert project instance into JSON-serializable dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "admin_id": self.admin_id,
            "status": self.status,
            "budget": float(self.budget) if self.budget is not None else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "is_sensitive": self.is_sensitive,
            "payment_status": self.payment_status,
            "project_type": self.project_type,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "matched_at": self.matched_at.isoformat() if self.matched_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancellation_reason": self.cancellation_reason,
            "required_skills": [rs.to_dict() for rs in self.required_skills],
            "deliverables": [
                {
                    "id": d.id,
                    "title": d.title,
                    "status": d.status,
                    "version_number": getattr(d, "version_number", None),
                }
                for d in self.deliverables
            ],
            "progress": self._calculate_progress(),
        }


# -------------------------------------------------------------------
# ProjectSkill Model
# -------------------------------------------------------------------
class ProjectSkill(db.Model):
    __tablename__ = "project_skills"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    # Keep nullable until Skill model is active (or wire to skills.id later)
    # skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    skill_id = db.Column(db.Integer, nullable=True)

    required_proficiency = db.Column(db.String(50), default="intermediate")

    # Relationship to parent project
    project = db.relationship("Project", back_populates="required_skills")
    # skill = db.relationship("Skill")  # enable when Skill model exists

    __table_args__ = (
        db.UniqueConstraint("project_id", "skill_id", name="uq_project_skill"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "skill_id": self.skill_id,
            "required_proficiency": self.required_proficiency,
        }
