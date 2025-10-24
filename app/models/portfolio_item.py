"""
Portfolio Item Model - Auto-generated Portfolio
Owner: Caleb
Description: Approved projects automatically added to freelancer portfolios.
"""

from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY

from app.extensions import db


class PortfolioItem(db.Model):
    __tablename__ = "portfolio_items"

    id = db.Column(db.Integer, primary_key=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_image_url = db.Column(db.String(255), nullable=True)
    project_url = db.Column(db.String(255), nullable=True)
    tags = db.Column(ARRAY(db.String), nullable=True)

    display_order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    freelancer = db.relationship("User", backref=db.backref("portfolio_items", lazy=True))
    project = db.relationship("Project", backref=db.backref("portfolio_item", uselist=False))

    def __repr__(self):
        return f"<PortfolioItem {self.id} {self.title} Project:{self.project_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "freelancer_id": self.freelancer_id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "cover_image_url": self.cover_image_url,
            "project_url": self.project_url,
            "tags": self.tags,
            "display_order": self.display_order,
            "is_featured": self.is_featured,
            "is_visible": self.is_visible,
            "created_at": self.created_at.isoformat(),
        }
