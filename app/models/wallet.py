"""
Wallet Models - User Balances and Transaction History
Owner: Caleb
Description:
Manages user wallet balances and transaction records (deposits, payments, refunds, releases, etc.).
"""

from datetime import datetime
from decimal import Decimal

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
        """Add funds to wallet with proper Decimal conversion"""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        amount_decimal = Decimal(str(amount))
        self.balance += amount_decimal
        db.session.commit()  

    def debit(self, amount):
        """Remove funds from wallet with proper Decimal conversion"""
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        amount_decimal = Decimal(str(amount))
        if self.balance < amount_decimal:
            raise ValueError("Insufficient balance")
        self.balance -= amount_decimal
        db.session.commit() 