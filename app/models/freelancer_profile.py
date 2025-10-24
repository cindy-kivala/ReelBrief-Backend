"""
Freelancer Profile Model
Owner: Ryan
Description: Extended profile for freelancers with CV, skills, and availability status.
"""

from datetime import datetime
from app.extensions import db


class FreelancerProfile(db.Model):
    __tablename__ = "freelancer_profiles"

    # -------------------- Core Fields --------------------
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    bio = db.Column(db.Text)
    cv_url = db.Column(db.String(255))
    cv_filename = db.Column(db.String(255))
    cv_uploaded_at = db.Column(db.DateTime)
    application_status = db.Column(db.String(50), default="pending")  # pending, approved, rejected
    rejection_reason = db.Column(db.Text)
    open_to_work = db.Column(db.Boolean, default=True)
    hourly_rate = db.Column(db.Numeric(10, 2))
    portfolio_url = db.Column(db.String(255))
    years_experience = db.Column(db.Integer)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -------------------- Relationships --------------------
    user = db.relationship("User", back_populates="freelancer_profile")

    # -------------------- Methods --------------------
    def to_dict(self):
        """Return a JSON-serializable freelancer profile representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bio": self.bio,
            "cv_url": self.cv_url,
            "cv_filename": self.cv_filename,
            "application_status": self.application_status,
            "rejection_reason": self.rejection_reason,
            "open_to_work": self.open_to_work,
            "hourly_rate": float(self.hourly_rate) if self.hourly_rate else None,
            "portfolio_url": self.portfolio_url,
            "years_experience": self.years_experience,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<FreelancerProfile user_id={self.user_id} status={self.application_status}>"
