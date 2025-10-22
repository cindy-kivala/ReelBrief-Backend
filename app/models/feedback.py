"""
Feedback Model - Structured Revision Requests
Owner: Cindy
Description: Client feedback with priority levels and threaded comments
"""

from datetime import datetime

from app.extensions import db

class Feedback(db.Model):
    __tablename__ = 'feedback'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    deliverable_id = db.Column(db.Integer, db.ForeignKey('deliverables.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)  # For threaded replies
    
# Relationships:
# - feedback belongs to deliverable
# - feedback belongs to author (User)
# - feedback has many replies (self-referential)
     # Relationships
    deliverable = db.relationship('Deliverable', back_populates='feedback_items')
    author = db.relationship('User', foreign_keys=[user_id], backref='feedback_given')
    
#
# Methods:
# - to_dict()
#
# Example:
# class Feedback(db.Model):
#     __tablename__ = 'feedback'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields
