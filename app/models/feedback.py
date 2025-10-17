"""
Feedback Model - Structured Revision Requests
Owner: Cindy
Description: Client feedback with priority levels and threaded comments
"""

from app.extensions import db
from datetime import datetime

# TODO: Cindy - Implement Feedback model
#
# Required fields:
# - id (Primary Key)
# - deliverable_id (Foreign Key to deliverables)
# - user_id (Foreign Key to users)
# - feedback_type (comment, revision, approval)
# - content (Text, Not Null)
# - priority (low, medium, high)
# - is_resolved (Boolean, default False)
# - parent_feedback_id (Foreign Key to feedback, for threaded replies)
# - created_at, resolved_at
#
# Relationships:
# - feedback belongs to deliverable
# - feedback belongs to author (User)
# - feedback has many replies (self-referential)
#
# Methods:
# - to_dict()
#
# Example:
# class Feedback(db.Model):
#     __tablename__ = 'feedback'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields