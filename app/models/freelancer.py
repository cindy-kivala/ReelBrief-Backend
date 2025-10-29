# app/models/freelancer.py
from datetime import datetime
from app.extensions import db

class Freelancer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    bio = db.Column(db.Text)
    cv_url = db.Column(db.String(300))
    portfolio_url = db.Column(db.String(300))
    years_experience = db.Column(db.Integer, default=0)
    hourly_rate = db.Column(db.Float, default=0.0)
    application_status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    rejection_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
