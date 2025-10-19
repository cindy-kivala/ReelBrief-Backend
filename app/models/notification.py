"""
Notification Model - Email & In-App Notifications
Owner: Caleb
Description: Tracks notifications sent to users with email status
"""

from datetime import datetime

from app.extensions import db

# TODO: Caleb - Implement Notification model
#
# Required fields:
# - id (Primary Key)
# - user_id (Foreign Key to users)
# - type (e.g., 'project_assigned', 'payment_received', 'deadline_reminder')
# - title, message
# - related_project_id (Foreign Key to projects, nullable)
# - related_deliverable_id (Foreign Key to deliverables, nullable)
# - is_read (Boolean, default False)
# - is_emailed (Boolean, default False)
# - email_sent_at
# - created_at
#
# Indexes:
# - (user_id, is_read) for fast unread queries
#
# Relationships:
# - notification belongs to user
# - notification optionally links to project/deliverable
#
# Methods:
# - to_dict()
#
# Example:
# class Notification(db.Model):
#     __tablename__ = 'notifications'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields
