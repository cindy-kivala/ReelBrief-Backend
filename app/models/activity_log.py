"""
Activity Log Model - Audit Trail
Owner: Caleb
Description: Tracks all important actions in the system for auditing.
"""

from datetime import datetime

from sqlalchemy.dialects.postgresql import INET, JSONB

from app.extensions import db


class ActivityLog(db.Model):
    __tablename__ = "activity_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    action = db.Column(db.String)
    resource_type = db.Column(db.String)
    resource_id = db.Column(db.Integer)
    details = db.Column(JSONB)
    ip_address = db.Column(INET)
    user_agent = db.Column(db.String)
    # created_at = db.Column(db.DateTime, datetime.now())
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"<ActivityLog {self.id} {self.action} {self.resource_type}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat(),
        }
