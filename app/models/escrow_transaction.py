# app/models/escrow.py
"""
Escrow Transaction Model - Payment Tracking
Owner: Caleb
Description: Tracks payment flow from client → escrow → freelancer.
"""

from datetime import datetime
from app.extensions import db


class EscrowTransaction(db.Model):
    __tablename__ = "escrow_transactions"

    id = db.Column(db.Integer, primary_key=True)

    # One-to-one FK to projects.id (unique enforces 1:1 at DB level)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default="USD", nullable=False)
    status = db.Column(
        db.String(20), default="held", nullable=False  # held, released, refunded, disputed
    )

    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_url = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)

    held_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime, nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Use back_populates (no backref) to avoid name collision with Project.escrow_transaction
    project = db.relationship(
        "Project",
        back_populates="escrow_transaction",
        lazy=True,
    )

    client = db.relationship("User", foreign_keys=[client_id])
    freelancer = db.relationship("User", foreign_keys=[freelancer_id])
    admin = db.relationship("User", foreign_keys=[admin_id])

    def __repr__(self):
        return f"<EscrowTransaction {self.id} Project:{self.project_id} ${self.amount} Status:{self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "project_title": self.project.title if self.project else "Unknown Project",
            "client_id": self.client_id,
            "client_name": (
                f"{self.client.first_name} {self.client.last_name}" if self.client else "Unknown"
            ),
            "freelancer_id": self.freelancer_id,
            "freelancer_name": (
                f"{self.freelancer.first_name} {self.freelancer.last_name}"
                if self.freelancer
                else "Unknown"
            ),
            "admin_id": self.admin_id,
            "amount": float(self.amount) if self.amount is not None else None,
            "currency": self.currency,
            "status": self.status,
            "invoice_number": self.invoice_number,
            "invoice_url": self.invoice_url,
            "payment_method": self.payment_method,
            "held_at": self.held_at.isoformat() if self.held_at else None,
            "released_at": self.released_at.isoformat() if self.released_at else None,
            "paid_at": (
                self.released_at.isoformat() if self.released_at else (self.held_at.isoformat() if self.held_at else None)
            ),
            "notes": self.notes,
        }
