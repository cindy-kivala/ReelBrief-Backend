"""
Deliverable Model - Version Control for Project Files
Owner: Cindy
Description: Tracks file uploads with version control and Cloudinary integration
"""

from datetime import datetime

from app.extensions import db



# TODO: Cindy - Implement Deliverable model
#

# Required fields: 
# - id (Primary Key)
# - project_id (Foreign Key to projects)
class Deliverable(db.Model):
    __tablename__ = 'deliverables'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

# - version_number (Integer, default 1)
    version_number = db.Column(db.Integer, nullable=False, default=1)

# - file_url (Not Null, from Cloudinary)
# - file_type (image, video, document)
# - file_size (bytes)
# - cloudinary_public_id
# - thumbnail_url (for images/videos)
    file_url = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(50))  # 'image', 'video', 'document'
    file_size = db.Column(db.Integer)  # bytes
    cloudinary_public_id = db.Column(db.String(255))
    thumbnail_url = db.Column(db.Text)

# - title, description
# - change_notes (what changed from previous version)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    change_notes = db.Column(db.Text)  # What changed from previous version

# - status (pending, approved, rejected, revision_requested)
    status = db.Column(
        db.String(20), 
        default='pending',
        nullable=False
    ) 
    
# Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = db.Column(db.DateTime, nullable=True)
# - uploaded_by (Foreign Key to users)
# - uploaded_at
# - reviewed_at, reviewed_by (Foreign Key to users)
#
# Relationships:
# - deliverable belongs to project
# - deliverable has many feedback_items
# - deliverable belongs to uploader (User)
# - deliverable belongs to reviewer (User)
    # project = db.relationship('Project', back_populates='deliverables')
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_deliverables')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_deliverables')
    feedback_items = db.relationship('Feedback', back_populates='deliverable', cascade='all, delete-orphan')

# indexes for faster queries
    __table_args__ = (
        db.Index('idx_deliverables_project', 'project_id'),
        db.Index('idx_deliverables_version', 'project_id', 'version_number'),
    )
    
# Methods:
# - to_dict()
#
# Example:
# class Deliverable(db.Model):
#     __tablename__ = 'deliverables'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields

# Merge line: Ryan - Monica - Cindy - Caleb
