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


class PortfolioItem(db.Model):
    __tablename__ = "portfolio_items"
    id = db.Column(db.Integer, primary_key = True)
    freelancer_id = db.Column(db.Integer,db.ForeignKey("freelancer.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    title = db.Column(db.String)
    description = db.Column(db.String)
    cover_image_url = db.Column(db.String ,nullable = True)
    project_url = db.Column(db.String)
    tags = db.Column(ARRAY(db.String))
    display_order = db.Column(db.Integer)
    is_featured = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, datetime.now())

    def __repr__(self):
        return f"<PortfolioItem {self.id} {self.title} {self.project_id} {self.description}>"