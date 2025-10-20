"""
Review Model - Client Feedback on Freelancers
Owner: Caleb
Description: Star ratings and reviews for completed projects
"""

from datetime import datetime

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
# Example:
# class Review(db.Model):
#     __tablename__ = 'reviews'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields
