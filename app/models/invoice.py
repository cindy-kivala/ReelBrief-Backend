"""
Invoice Model - Billing and Payment Record
Owner: Caleb
Description: Represents an official payment request between freelancer/agency and client.
"""

from datetime import datetime

from app.extensions import db


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default="USD", nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(
        db.String(20),
        default="unpaid",
        nullable=False,
    )  # unpaid, paid, overdue, cancelled

    pdf_url = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Optional link to EscrowTransaction
    escrow_id = db.Column(db.Integer, db.ForeignKey("escrow_transactions.id"), nullable=True)
    escrow = db.relationship("EscrowTransaction", backref="invoice", uselist=False)

    def __repr__(self):
        return f"<Invoice {self.invoice_number} | {self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "client_id": self.client_id,
            "freelancer_id": self.freelancer_id,
            "invoice_number": self.invoice_number,
            "amount": float(self.amount),
            "currency": self.currency,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "status": self.status,
            "pdf_url": self.pdf_url,
            "notes": self.notes,
        }
