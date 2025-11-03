# app/models/escrow.py
"""
EscrowTransaction Model - Secure Funds Movement
Owner: Caleb
Description: Tracks all money held and released in escrow between clients and freelancers.
"""

from datetime import datetime
from app.extensions import db


class EscrowTransaction(db.Model):
    __tablename__ = "escrow_transactions"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)  # Restored
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Client
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Freelancer

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="held", nullable=False)  # held, released, refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    released_at = db.Column(db.DateTime, nullable=True)

    # Link back to Project
    project = db.relationship("Project", back_populates="escrow_transactions")

    # Explicit relationship to Invoice
    invoice = db.relationship(
        "Invoice", back_populates="escrow_transaction", foreign_keys=[invoice_id]
    )

    # Relationships to users
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_escrow_transactions")

    receiver = db.relationship(
        "User", foreign_keys=[receiver_id], backref="received_escrow_transactions"
    )

    def __repr__(self):
        return f"<EscrowTransaction {self.id} | {self.status}>"

    def to_dict(self):
        """Serialize escrow transaction for frontend"""
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "project_id": self.project_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "amount": float(self.amount),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "released_at": self.released_at.isoformat() if self.released_at else None,
        }
