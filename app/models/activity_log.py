# """
# Activity Log Model - Audit Trail
# Owner: Caleb
# Description: Tracks all important actions in the system for auditing
# """

# from datetime import datetime
# from sqlalchemy.dialects.postgresql import INET, JSONB
# from app.extensions import db


# class ActivityLog(db.Model):
#     __tablename__ = "activity_log"

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
#     action = db.Column(db.String(255), nullable=False)
#     resource_type = db.Column(db.String(100))
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
