"""
Feedback Model - Structured Revision Requests
Owner: Cindy
Description: Client feedback with priority levels and threaded comments
"""

from datetime import datetime
from app.extensions import db
from app.models.deliverable import Deliverable  # ✅ Direct import — breaks circular dependency
from app.models.user import User  # ✅ Import only what’s needed


class Feedback(db.Model):
    __tablename__ = "feedback"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    deliverable_id = db.Column(
        db.Integer, db.ForeignKey("deliverables.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_feedback_id = db.Column(
        db.Integer, db.ForeignKey("feedback.id"), nullable=True
    )  # For threaded replies

    # Feedback Content
    feedback_type = db.Column(db.String(20), nullable=False)  # comment, revision, approval
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20))  # low, medium, high

    # Status
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    deliverable = db.relationship("Deliverable", back_populates="feedback_items")
    author = db.relationship("User", foreign_keys=[user_id], backref="feedback_given")

    # Self-referential relationship for threaded comments
    replies = db.relationship(
        "Feedback",
        backref=db.backref("parent_feedback", remote_side=[id]),
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.Index("idx_feedback_deliverable", "deliverable_id"),
        db.Index("idx_feedback_user", "user_id"),
    )

    def __repr__(self):
        return f"<Feedback {self.id} - {self.feedback_type} on Deliverable {self.deliverable_id}>"

    def to_dict(self, include_replies=True):
        data = {
            "id": self.id,
            "deliverable_id": self.deliverable_id,
            "user_id": self.user_id,
            "parent_feedback_id": self.parent_feedback_id,
            "feedback_type": self.feedback_type,
            "content": self.content,
            "priority": self.priority,
            "is_resolved": self.is_resolved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "author": (
                {
                    "id": self.author.id,
                    "first_name": self.author.first_name,
                    "last_name": self.author.last_name,
                    "email": self.author.email,
                    "role": self.author.role,
                }
                if self.author
                else None
            ),
        }

        if include_replies and self.replies:
            data["replies"] = [r.to_dict(include_replies=False) for r in self.replies]

        return data

    def resolve(self):
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
        db.session.commit()

    def unresolve(self):
        self.is_resolved = False
        self.resolved_at = None
        db.session.commit()

    @staticmethod
    def get_feedback_for_deliverable(deliverable_id, include_resolved=True):
        query = Feedback.query.filter_by(
            deliverable_id=deliverable_id, parent_feedback_id=None
        )
        if not include_resolved:
            query = query.filter_by(is_resolved=False)
        return query.order_by(Feedback.created_at.desc()).all()

    @staticmethod
    def get_unresolved_count(deliverable_id):
        return Feedback.query.filter_by(
            deliverable_id=deliverable_id, is_resolved=False
        ).count()
