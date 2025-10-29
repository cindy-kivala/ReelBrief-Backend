from datetime import datetime
from app.extensions import db  # Add this import

class Project(db.Model):
    __tablename__ = 'projects'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic fields
    title = db.Column(db.String(255), nullable=False, default='Test Project')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Client/Freelancer/Admin relationships
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Status and project details
    status = db.Column(db.String(30), default='submitted')
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    is_sensitive = db.Column(db.Boolean, default=False)
    payment_status = db.Column(db.String(20), default='unpaid')
    project_type = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='medium')
    
    # Timestamps
    matched_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    
    # Relationships
    deliverables = db.relationship('Deliverable', back_populates='project', lazy=True)
    
    def __repr__(self):
        return f"<Project {self.id}: {self.title}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'is_sensitive': self.is_sensitive,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'client_id': self.client_id,
            'freelancer_id': self.freelancer_id,
            'admin_id': self.admin_id,
            'budget': float(self.budget) if self.budget else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'payment_status': self.payment_status,
            'project_type': self.project_type,
            'priority': self.priority,
            'matched_at': self.matched_at.isoformat() if self.matched_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_reason': self.cancellation_reason
        }