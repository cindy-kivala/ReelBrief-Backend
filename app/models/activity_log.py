"""
Activity Log Model - Audit Trail
Owner: Caleb
Description: Tracks all important actions in the system for auditing.
"""

# from datetime import datetime
# from sqlalchemy.dialects.postgresql import INET, JSONB
# from app.extensions import db


# class ActivityLog(db.Model):
#     __tablename__ = "activity_log"

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
#     action = db.Column(db.String)
#     resource_type = db.Column(db.String)
#     resource_id = db.Column(db.Integer)
#     details = db.Column(JSONB)
#     ip_address = db.Column(INET)
#     user_agent = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     __table_args__ = (
#         db.Index("idx_user_id", "user_id"),
#         db.Index("idx_resource", "resource_type", "resource_id"),
#     )

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "action": self.action,
#             "resource_type": self.resource_type,
#             "resource_id": self.resource_id,
#             "details": self.details,
#             "ip_address": self.ip_address,
#             "user_agent": self.user_agent,
#             "created_at": self.created_at.isoformat() if self.created_at else None,
#         }

#     def __repr__(self):
#         return f"<ActivityLog {self.id} {self.action} {self.resource_type}>"

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "action": self.action,
#             "resource_type": self.resource_type,
#             "resource_id": self.resource_id,
#             "user_name": f"{self.user.first_name} {self.user.last_name}" if self.user else "System",
#             "created_at": self.created_at.isoformat() if self.created_at else None,
#             "details": self.details or {},
#         }


from app import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add relationship to User
    user = db.relationship('User', backref='activity_logs', lazy='joined')
    
    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "user_name": f"{self.user.first_name} {self.user.last_name}" if self.user else "System",
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "details": self.details or {},
        }