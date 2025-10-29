# app/models/project.py
from datetime import datetime

from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(
        db.String(50), default="submitted"
    )  # submitted, in_progress, pending_review, completed
    budget = db.Column(db.Numeric(10, 2), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    is_sensitive = db.Column(db.Boolean, default=False)
    payment_status = db.Column(db.String(20), default="unpaid")  # unpaid, in_escrow, released
    project_type = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    matched_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)

    # Relationships
    client = db.relationship("User", foreign_keys=[client_id], backref="client_projects")
    freelancer = db.relationship(
        "User", foreign_keys=[freelancer_id], backref="freelancer_projects"
    )
    admin = db.relationship("User", foreign_keys=[admin_id])
    deliverables = db.relationship("Deliverable", back_populates="project", lazy=True)
    escrow_transaction = db.relationship("EscrowTransaction", backref="project", uselist=False)

    def __repr__(self):
        return f"<Project {self.id}: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "budget": float(self.budget) if self.budget else 0.0,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "is_sensitive": self.is_sensitive,
            "payment_status": self.payment_status,
            "project_type": self.project_type,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "requested_at": self.created_at.isoformat() if self.created_at else None,
            "client_name": (
                f"{self.client.first_name} {self.client.last_name}" if self.client else "Unknown"
            ),
            "freelancer_name": (
                f"{self.freelancer.first_name} {self.freelancer.last_name}"
                if self.freelancer
                else "Unassigned"
            ),
            "progress": self._calculate_progress(),
        }

    def _calculate_progress(self):
        if not self.deliverables:
            return 0
        total = len(self.deliverables)
        completed = len([d for d in self.deliverables if d.status == "approved"])
        return int((completed / total) * 100) if total > 0 else 0
