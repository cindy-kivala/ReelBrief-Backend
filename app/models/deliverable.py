"""
Deliverable Model - Version Control for Project Files
Owner: Cindy
Description: Tracks file uploads with version control and Cloudinary integration
"""

from datetime import datetime
from app.extensions import db

class Deliverable(db.Model):
    __tablename__ = 'deliverables'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    project_id = db.Column(db.Integer, nullable=False) # ADD db.ForeignKey('projects.id', ondelete='CASCADE') after Project merge
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

# - version_number (Integer, default 1)
    version_number = db.Column(db.Integer, nullable=False, default=1)

# - Files
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

#
# Relationships:
# - deliverable belongs to project
# - deliverable has many feedback_items
# - deliverable belongs to uploader (User)
# - deliverable belongs to reviewer (User)
    # project = db.relationship('Project', back_populates='deliverables')
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_deliverables')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reviewed_deliverables')
    # feedback_items = db.relationship('Feedback', back_populates='deliverable', cascade='all, delete-orphan')

# indexes for faster queries
    __table_args__ = (
        db.Index('idx_deliverables_project', 'project_id'),
        db.Index('idx_deliverables_version', 'project_id', 'version_number'),
    )

# Methods:
    def __repr__(self):
        return f'<Deliverable {self.id} v{self.version_number} - {self.title}>'

    def to_dict(self, include_feedback=False):
        """Convert deliverable to dictionary representation"""
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'version_number': self.version_number,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'cloudinary_public_id': self.cloudinary_public_id,
            'thumbnail_url': self.thumbnail_url,
            'title': self.title,
            'description': self.description,
            'change_notes': self.change_notes,
            'status': self.status,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': self.reviewed_by,
            'uploader': {
                'id': self.uploader.id,
                'first_name': self.uploader.first_name,
                'last_name': self.uploader.last_name,
                'email': self.uploader.email
            } if self.uploader else None,
            'reviewer': {
                'id': self.reviewer.id,
                'first_name': self.reviewer.first_name,
                'last_name': self.reviewer.last_name
            } if self.reviewer else None
        }
        
        #ADD AFTER FEEDBACK IS READY
        # if include_feedback:
        #     data['feedback'] = [f.to_dict() for f in self.feedback_items]
        
        return data

    @staticmethod
    def get_next_version_number(project_id):
        """Get the next version number for a project"""
        latest = Deliverable.query.filter_by(project_id=project_id).order_by(Deliverable.version_number.desc()).first()
        return (latest.version_number + 1) if latest else 1

    def approve(self, reviewed_by_id): #client will be approving after reviewing
        """Approve this deliverable"""
        self.status = 'approved'
        self.reviewed_by = reviewed_by_id
        self.reviewed_at = datetime.utcnow()
        db.session.commit()

    def request_revision(self): #Remeberto add this feaure better
        """Mark deliverable as needing revision"""
        self.status = 'revision_requested'
        self.reviewed_at = datetime.utcnow()
        db.session.commit()

    def reject(self, reviewed_by_id):
        """Reject this deliverable"""
        self.status = 'rejected'
        self.reviewed_by = reviewed_by_id
        self.reviewed_at = datetime.utcnow()
        db.session.commit()
