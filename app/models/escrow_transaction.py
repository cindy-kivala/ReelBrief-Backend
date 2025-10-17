"""
Escrow Transaction Model - Payment Tracking
Owner: Caleb
Description: Tracks payment flow from client → escrow → freelancer
"""

from app.extensions import db
from datetime import datetime

# TODO: Caleb - Implement EscrowTransaction model
#
# Required fields:
# - id (Primary Key)
# - project_id (Foreign Key to projects, Unique - one transaction per project)
# - client_id (Foreign Key to users)
# - freelancer_id (Foreign Key to users)
# - admin_id (Foreign Key to users)
# - amount, currency (default USD)
# - status (held, released, refunded, disputed)
# - invoice_number (Unique)
# - invoice_url
# - payment_method
# - held_at, released_at, refunded_at
# - notes
#
# Relationships:
# - transaction belongs to project (one-to-one)
# - transaction belongs to client, freelancer, admin (Users)
#
# Methods:
# - to_dict()
#
# Example:
# class EscrowTransaction(db.Model):
#     __tablename__ = 'escrow_transactions'
#     id = db.Column(db.Integer, primary_key=True)
#     # ... rest of fields

#Caleb before you merge anything make sure the first three From Ryan to me have merge to avoid breaks and conflicts