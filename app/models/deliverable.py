"""
Deliverable Model - Version Control for Project Files
Owner: Cindy
Description: Tracks file uploads with version control and Cloudinary integration
"""

from app.extensions import db
from datetime import datetime

class Deliverable(db.Model):
    __tablename__ = "deliverables"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(255))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "file_url": self.file_url,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }
# TODO: Cindy - Implement Deliverable model
#
# Required fields:
# - id (Primary Key)
# - project_id (Foreign Key to projects)
# - version_number (Integer, default 1)
# - file_url (Not Null, from Cloudinary)
# - file_type (image, video, document)
# - file_size (bytes)
# - cloudinary_public_id
# - thumbnail_url (for images/videos)
# - title, description
# - change_notes (what changed from previous version)
# - status (pending, approved, rejected, revision_requested)
# - uploaded_by (Foreign Key to users)
# - uploaded_at
# - reviewed_at, reviewed_by (Foreign Key to users)
#
# Relationships:
# - deliverable belongs to project
# - deliverable has many feedback_items
# - deliverable belongs to uploader (User)
# - deliverable belongs to reviewer (User)
#
# Methods:
# - to_dict()
#
# Example:
# class Deliverable(db.Model):
#     __tablename__ = 'deliverables'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields

# Merge line: Ryan - Monica - Cindy - Caleb
