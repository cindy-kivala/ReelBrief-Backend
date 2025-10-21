"""
Notification Model - Email & In-App Notifications
Owner: Ryan
Description: Tracks notifications sent to users with email status.
"""

from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    # -------------------- Core Fields --------------------
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    type = db.Column(db.String(50), nullable=False, default="general")
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

    related_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)
    related_deliverable_id = db.Column(db.Integer, db.ForeignKey("deliverables.id"), nullable=True)

    is_read = db.Column(db.Boolean, default=False)
    is_emailed = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -------------------- Relationships --------------------
    user = db.relationship("User", back_populates="notifications")

    # Index for fast unread queries
    __table_args__ = (db.Index("idx_user_unread", "user_id", "is_read"),)

    # -------------------- Methods --------------------
    def to_dict(self):
        """Return a JSON-serializable notification representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "related_project_id": self.related_project_id,
            "related_deliverable_id": self.related_deliverable_id,
            "is_read": self.is_read,
            "is_emailed": self.is_emailed,
            "email_sent_at": self.email_sent_at.isoformat() if self.email_sent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Notification user_id={self.user_id} type={self.type}>"
