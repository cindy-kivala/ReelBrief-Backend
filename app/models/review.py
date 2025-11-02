"""
Review Model - Client Feedback on Freelancers
Owner: Caleb
Description: Star ratings and reviews for completed projects
"""

from datetime import datetime

from sqlalchemy import CheckConstraint

from app.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    rating = db.Column(
        db.Integer,
        CheckConstraint("rating >= 1 AND rating <= 5"),
        nullable=False,
    )
    communication_rating = db.Column(
        db.Integer,
        CheckConstraint("communication_rating >= 1 AND communication_rating <= 5"),
        nullable=True,
    )
    quality_rating = db.Column(
        db.Integer,
        CheckConstraint("quality_rating >= 1 AND quality_rating <= 5"),
        nullable=True,
    )
    timeliness_rating = db.Column(
        db.Integer,
        CheckConstraint("timeliness_rating >= 1 AND timeliness_rating <= 5"),
        nullable=True,
    )

    review_text = db.Column(db.Text, nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    project = db.relationship(
        "Project",
        backref=db.backref("review", uselist=False, cascade="all, delete-orphan"),
    )
    client = db.relationship(
        "User",
        foreign_keys=[client_id],
        backref=db.backref("client_reviews", lazy=True, cascade="all, delete-orphan"),
    )
    freelancer = db.relationship(
        "User",
        foreign_keys=[freelancer_id],
        backref=db.backref("freelancer_reviews", lazy=True, cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<Review {self.id} Freelancer:{self.freelancer_id} Rating:{self.rating}>"

    def average_rating(self):
        ratings = [
            r
            for r in [self.communication_rating, self.quality_rating, self.timeliness_rating]
            if r is not None
        ]
        return round(sum(ratings) / len(ratings), 2) if ratings else float(self.rating)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "rating": self.rating,
            "communication_rating": self.communication_rating,
            "quality_rating": self.quality_rating,
            "timeliness_rating": self.timeliness_rating,
            "average_rating": self.average_rating(),
            "review_text": self.review_text,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat(),
        }
