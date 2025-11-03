"""
WalletTransaction Model - Ledger for All Wallet Activities
Owner: Caleb
Description:
Records each deposit, payment, release, refund, and withdrawal in the system.
"""

from datetime import datetime

from app.extensions import db


class WalletTransaction(db.Model):
    __tablename__ = "wallet_transactions"

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(
        db.String(20), nullable=False, doc="deposit, payment, release, refund, withdraw"
    )
    description = db.Column(db.String(255), nullable=True)
    reference_id = db.Column(
        db.Integer, nullable=True, doc="Optional link to invoice or escrow transaction"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WalletTransaction {self.transaction_type} {self.amount}>"

    def to_dict(self):
        """Serialize transaction data for API"""
        return {
            "id": self.id,
            "wallet_id": self.wallet_id,
            "amount": float(self.amount),
            "transaction_type": self.transaction_type,
            "description": self.description,
            "reference_id": self.reference_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
