"""
Escrow Transaction Model - Payment Tracking
Owner: Caleb
Description: Tracks payment flow from client → escrow → freelancer
"""

from datetime import datetime

from app.extensions import db

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
# - notes -ask Cindy about this
#
# Relationships:
# - transaction belongs to project (one-to-one)
# - transaction belongs to client, freelancer, admin (Users)
#
# Methods:
# - to_dict()


class EscrowTransaction(db.Model):
    __tablename__ = 'escrow_transactions'
    id = db.Column(db.Integer, primary_key = True)
    project_id = db.Column(db.Integer, )
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable = False)
    freelancer_id = db.Column(db.Integer, db.relationship("freelancer.id"), nullable = False)
    admin_id = db.Column(db.Integer, db.relationship("admin.id"), nullable = False)

    amount = db.Column(db.Integer) #set the default as USD
    status = db.Column(db.String)
    invoice_number = db.Column(db.Integer, unique = True)
    invoice_url = db.Column(db.String)

    held_at = db.Column(db.String, datetime.now())
    released_at = db.Column(db.String,datetime.now())

# Caleb before you merge anything make sure the first three From Ryan to me have merge to avoid breaks and conflicts
