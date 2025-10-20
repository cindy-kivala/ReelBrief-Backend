"""
Activity Log Model - Audit Trail
Owner: Caleb
Description: Tracks all important actions in the system for auditing
"""

from datetime import datetime

from sqlalchemy.dialects.postgresql import INET, JSONB

from app.extensions import db

# TODO: Caleb - Implement ActivityLog model
#
# Required fields:
# - id (Primary Key)
# - user_id (Foreign Key to users, nullable for system actions)
# - action (String, e.g., 'project_created', 'deliverable_uploaded')
# - resource_type (String, e.g., 'project', 'deliverable', 'user')
# - resource_id (Integer, ID of the affected resource)
# - details (JSONB, flexible metadata storage)
# - ip_address (INET type for PostgreSQL)
# - user_agent (Text)
# - created_at
#
# Indexes:
# - user_id for user activity queries
# - (resource_type, resource_id) for resource history
#
# Relationships:
# - activity_log belongs to user
#
# Methods:
# - to_dict()
#
# Example:
# class ActivityLog(db.Model):
#     __tablename__ = 'activity_log'
#     id = db.Column(db.Integer, primary_key=True)
#     details = db.Column(JSONB)
#     ip_address = db.Column(INET)
#     # ... rest of fields
