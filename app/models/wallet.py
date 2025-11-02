"""
Wallet Models - User Balances and Transaction History
Owner: Caleb
Description:
Manages user wallet balances and transaction records (deposits, payments, refunds, releases, etc.).
"""

from datetime import datetime

from app.extensions import db


class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    currency = db.Column(db.String(10), default="USD", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("wallet", uselist=False))
    transactions = db.relationship(
        "WalletTransaction", backref="wallet", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Wallet User={self.user_id} Balance={self.balance} {self.currency}>"

    def to_dict(self):
        """Serialize wallet data for API"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": float(self.balance),
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def credit(self, amount):
        """Add funds to wallet"""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        self.balance += amount

    def debit(self, amount):
        """Remove funds from wallet"""
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        self.balance -= amount
