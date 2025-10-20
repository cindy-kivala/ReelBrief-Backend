"""
Portfolio Item Model - Auto-generated Portfolio
Owner: Caleb
Description: Approved projects automatically added to freelancer portfolios
"""

from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY

from app.extensions import db

# TODO: Caleb - Implement PortfolioItem model
#
# Required fields:
# - id (Primary Key)
# - freelancer_id (Foreign Key to freelancer_profiles)
# - project_id (Foreign Key to projects, Unique)
# - title, description
# - cover_image_url
# - project_url
# - tags (PostgreSQL ARRAY of text)
# - display_order (Integer for sorting)
# - is_featured (Boolean)
# - is_visible (Boolean, manual override)
# - created_at
#
# Relationships:
# - portfolio_item belongs to freelancer
# - portfolio_item belongs to project (one-to-one)
#
# Methods:
# - to_dict()
#
# Example:
# class PortfolioItem(db.Model):
#     __tablename__ = 'portfolio_items'
#     id = db.Column(db.Integer, primary_key=True)
#     tags = db.Column(ARRAY(db.Text))
#     # ... rest of fields
