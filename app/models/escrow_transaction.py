# """
# Escrow Transaction Model - Payment Tracking
# Owner: Caleb
# Description: Tracks payment flow from client → escrow → freelancer
# """

# from datetime import datetime
# from app.extensions import db


# class EscrowTransaction(db.Model):
#     __tablename__ = "escrow_transactions"

#     id = db.Column(db.Integer, primary_key=True)

#     # Foreign Keys
#     project_id = db.Column(db.Integer, db.ForeignKey("project.id"), unique=True, nullable=False)
#     client_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     freelancer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     admin_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

#     # Transaction details
#     amount = db.Column(db.Numeric(10, 2), nullable=False)
#     currency = db.Column(db.String(10), default="USD")
#     status = db.Column(db.String(50), default="held")
#     invoice_number = db.Column(db.String(50), unique=True)
#     invoice_url = db.Column(db.String)
#     payment_method = db.Column(db.String(50))
#     notes = db.Column(db.Text)

#     # Important timestamps
#     held_at = db.Column(db.DateTime, default=datetime.utcnow)
#     released_at = db.Column(db.DateTime)
#     refunded_at = db.Column(db.DateTime)

#     # Relationships
#     project = db.relationship("Project", backref=db.backref("escrow_transaction", uselist=False))
#     client = db.relationship("User", foreign_keys=[client_id], backref="client_transactions")
#     freelancer = db.relationship("User", foreign_keys=[freelancer_id], backref="freelancer_transactions")
#     admin = db.relationship("User", foreign_keys=[admin_id], backref="admin_transactions")

#     def __repr__(self):
#         return f"<EscrowTransaction {self.id} | ${self.amount} | {self.status}>"
