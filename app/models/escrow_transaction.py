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
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default="USD", nullable=False)
    status = db.Column(
        db.String(20), default="held", nullable=False
    )  # held, released, refunded, disputed

    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_url = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)

    held_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime, nullable=True)
    refunded_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    project = db.relationship("Project", backref=db.backref("escrow_transaction", uselist=False))
    client = db.relationship("User", foreign_keys=[client_id])
    freelancer = db.relationship("User", foreign_keys=[freelancer_id])
    admin = db.relationship("User", foreign_keys=[admin_id])

    def __repr__(self):
        return f"<EscrowTransaction {self.id} Project:{self.project_id} ${self.amount} Status:{self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "admin_id": self.admin_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status,
            "invoice_number": self.invoice_number,
            "invoice_url": self.invoice_url,
            "payment_method": self.payment_method,
            "held_at": self.held_at.isoformat() if self.held_at else None,
            "released_at": self.released_at.isoformat() if self.released_at else None,
            "refunded_at": self.refunded_at.isoformat() if self.refunded_at else None,
            "notes": self.notes,
        }
