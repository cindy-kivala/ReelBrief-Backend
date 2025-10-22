"""
Review Model - Client Feedback on Freelancers
Owner: Caleb
Description: Star ratings and reviews for completed projects
"""

from datetime import datetime

from sqlalchemy import CheckConstraint

from app.extensions import db

# TODO: Caleb - Implement Review model
#
# Required fields:
# - id (Primary Key)
# - project_id (Foreign Key to projects, Unique - one review per project)
# - client_id (Foreign Key to users)
# - freelancer_id (Foreign Key to users)
# - rating (Integer 1-5, overall rating)
# - communication_rating (Integer 1-5)
# - quality_rating (Integer 1-5)
# - timeliness_rating (Integer 1-5)
# - review_text (Text)
# - is_public (Boolean, default True)
# - created_at
#
# Relationships:
# - review belongs to project (one-to-one)
# - review belongs to client (User)
# - review belongs to freelancer (User)
#
# Methods:
# - to_dict()
# - average_rating() - calculates avg of sub-ratings
#


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    freelancer_id = db.Column(db.Integer, db.ForeignKey("freelancer.id"))
    rating = db.Column(db.Integer, CheckConstraint("rating >= 1 AND rating <= 5"), nullable=False)
    communication_rating = db.Column(
        db.Integer, CheckConstraint("communication_rating >= 1 AND communication_rating <= 5")
    )
    quality_rating = db.Column(
        db.Integer, CheckConstraint("quality_rating >= 1 AND quality_rating <=5")
    )
    timeliness_rating = db.Column(
        db.Integer, CheckConstraint("timeliness_rating >= 1 AND timeliness <= 5")
    )
    review_text = db.Column(db.String)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, datetime.now())

    def __repr__(self):
        return f"<Review {self.id} {self.freelancer_id} {self.rating} {self.review_text}"
