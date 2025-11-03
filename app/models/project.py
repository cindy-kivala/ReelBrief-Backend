# from datetime import datetime
# from app.extensions import db  # Add this import

# class Project(db.Model):
#     __tablename__ = "projects"

#     # -------------------- Primary Key --------------------
#     id = db.Column(db.Integer, primary_key=True)
    
#     # Basic fields
#     title = db.Column(db.String(255), nullable=False, default='Test Project')
#     description = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Client/Freelancer/Admin relationships
#     client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
#     # Status and project details
#     status = db.Column(db.String(30), default='submitted')
#     budget = db.Column(db.Numeric(10, 2), nullable=False)
#     deadline = db.Column(db.Date, nullable=False)
#     is_sensitive = db.Column(db.Boolean, default=False)
#     payment_status = db.Column(db.String(20), default='unpaid')
#     project_type = db.Column(db.String(50))
#     priority = db.Column(db.String(20), default='medium')
    
#     # Timestamps
#     matched_at = db.Column(db.DateTime)
#     started_at = db.Column(db.DateTime)
#     completed_at = db.Column(db.DateTime)
#     cancelled_at = db.Column(db.DateTime)
#     cancellation_reason = db.Column(db.Text)
    
#     # Relationships
#     deliverables = db.relationship('Deliverable', back_populates='project', lazy=True)
    
#     def __repr__(self):
#         return f"<Project {self.id}: {self.title}>"
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'title': self.title,
#             'description': self.description,
#             'status': self.status,
#             'is_sensitive': self.is_sensitive,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'client_id': self.client_id,
#             'freelancer_id': self.freelancer_id,
#             'admin_id': self.admin_id,
#             'budget': float(self.budget) if self.budget else None,
#             'deadline': self.deadline.isoformat() if self.deadline else None,
#             'payment_status': self.payment_status,
#             'project_type': self.project_type,
#             'priority': self.priority,
#             'matched_at': self.matched_at.isoformat() if self.matched_at else None,
#             'started_at': self.started_at.isoformat() if self.started_at else None,
#             'completed_at': self.completed_at.isoformat() if self.completed_at else None,
#             'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
#             'cancellation_reason': self.cancellation_reason
#         }


"""
Project Models
Owner: Monica
Description: Project management with status tracking, deliverables, and skill requirements.
UPDATED: Added approval workflow fields
"""

from datetime import datetime

from ..extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    #  Primary Key 
    id = db.Column(db.Integer, primary_key=True)

    # Core Info
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    #  Foreign Keys (linked users) 
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    status = db.Column(
        db.String(50), default="submitted"
    )  # submitted, in_progress, completed, etc.
    budget = db.Column(db.Numeric(10, 2), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    is_sensitive = db.Column(db.Boolean, default=False)
    payment_status = db.Column(
        db.String(50), default="unpaid"
    )  # unpaid, in_escrow, released, refunded
    project_type = db.Column(db.String(100))
    priority = db.Column(db.String(50), default="normal")

    #  Approval Workflow Fields 
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    assignment_requested = db.Column(db.Boolean, default=False)  # Client requests admin to assign
    assigned_at = db.Column(db.DateTime, nullable=True)

    #  Time Tracking 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    matched_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)

    #  Relationships 
    # Each project can have multiple required skills
    # -------------------- Relationships --------------------
    # Users
    # client = db.relationship("User", foreign_keys=[client_id], backref="client_projects")
    # freelancer = db.relationship("User", foreign_keys=[freelancer_id], backref="freelancer_projects")
    # admin = db.relationship("User", foreign_keys=[admin_id])

    # # Deliverables (one-to-many)
    # deliverables = db.relationship(
    #     "Deliverable",
    #     back_populates="project",
    #     cascade="all, delete-orphan",
    #     lazy=True,
    # )

    # Required skills (one-to-many)
    # required_skills = db.relationship(
    #     "ProjectSkill",
    #     back_populates="project",
    #     cascade="all, delete-orphan",
    # )

    # Caleb's relationships
    client = db.relationship("User", foreign_keys=[client_id], backref="client_projects")
    freelancer = db.relationship(
        "User", foreign_keys=[freelancer_id], backref="freelancer_projects"
    )
    admin = db.relationship("User", foreign_keys=[admin_id])
    
    #  Approver relationship
    approver = db.relationship("User", foreign_keys=[approved_by], backref="approved_projects")
    
    # Other relationships
    deliverables = db.relationship("Deliverable", back_populates="project", lazy=True)
    # escrow_transaction = db.relationship("EscrowTransaction", backref="project", uselist=False)

    # Placeholder one-to-one relationships (for future expansion)
    deliverables = db.relationship("Deliverable", back_populates="project", lazy=True)
    escrow_transactions = db.relationship(
        "EscrowTransaction", back_populates="project", cascade="all, delete-orphan"
    )
    portfolio_items = db.relationship(
        "PortfolioItem", back_populates="project", cascade="all, delete-orphan"
    )

    #  Methods 
    def to_dict(self):
        """Convert project instance into JSON-serializable dictionary."""
    # Escrow (one-to-one) — explicit two-sided mapping (no backref)
    # escrow_transaction = db.relationship(
    #     "EscrowTransaction",
    #     back_populates="project",
    #     uselist=False,
    # )

    # -------------------- Methods --------------------
    def _calculate_progress(self) -> int:
        """% of deliverables approved."""
        if not self.deliverables:
            return 0
        total = len(self.deliverables)
        approved = len([d for d in self.deliverables if getattr(d, "status", "") == "approved"])
        return int((approved / total) * 100) if total > 0 else 0

    def to_dict(self) -> dict:
        """Serialize for APIs."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "admin_id": self.admin_id,
            "status": self.status,
            "budget": float(self.budget) if self.budget is not None else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "is_sensitive": self.is_sensitive,
            "payment_status": self.payment_status,
            "project_type": self.project_type,
            "priority": self.priority,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),  
            # Caleb's format
            "matched_at": self.matched_at.isoformat() if self.matched_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancellation_reason": self.cancellation_reason,
            
            # Related data
            "required_skills": [rs.to_dict() for rs in self.required_skills],
            "client_name": (
                f"{self.client.first_name} {self.client.last_name}" if self.client else "Unknown"
            ),
            "freelancer_name": (
                f"{self.freelancer.first_name} {self.freelancer.last_name}"
                if self.freelancer
                else "Unassigned"
            ),
            
            # Include approver info if exists
            "approver_name": (
                f"{self.approver.first_name} {self.approver.last_name}"
                if self.approved_by and self.approver else None
            ),
            
            "progress": self._calculate_progress(),
            "deliverables": [
                {
                    "id": d.id,
                    "title": getattr(d, "title", None),
                    "status": getattr(d, "status", None),
                    "version_number": getattr(d, "version_number", None),
                }
                for d in self.deliverables
            ],
            "escrow": {
                "id": self.escrow_transaction.id,
                "status": self.escrow_transaction.status,
                "amount": float(self.escrow_transaction.amount),
            } if self.escrow_transaction else None,
        }

    def _calculate_progress(self):
        """Calculate project progress based on deliverables"""
        if not self.deliverables:
            return 0
        total = len(self.deliverables)
        completed = len([d for d in self.deliverables if d.status == "approved"])
        return int((completed / total) * 100) if total > 0 else 0

    def __repr__(self):
        return f"<Project {self.id}: {self.title}>"


# ProjectSkill Model

class ProjectSkill(db.Model):
    __tablename__ = "project_skills"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    required_proficiency = db.Column(db.String(50), default="intermediate")

    # Relationships
    project = db.relationship("Project", back_populates="required_skills")
    skill = db.relationship("Skill")

    __table_args__ = (db.UniqueConstraint("project_id", "skill_id", name="uq_project_skill"),)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "skill_id": self.skill_id,
            "skill_name": self.skill.name if self.skill else None,  # Include skill name
            "required_proficiency": self.required_proficiency,
        }
