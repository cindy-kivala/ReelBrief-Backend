"""
app/models/__init__.py
Owner: Ryan
Description: Central model registry for the ReelBrief backend.
"""
from pathlib import Path

from app.extensions import db

# from app.models.skill import Skill, FreelancerSkill
# from app.models.project import Project, ProjectSkill
from app.models.deliverable import Deliverable
from app.models.feedback import Feedback
from app.models.freelancer_profile import FreelancerProfile

# from app.models.escrow_transaction import EscrowTransaction
# from app.models.portfolio_item import PortfolioItem
from app.models.notification import Notification

# --- Explicit imports (required for Flask-Migrate) ---
from app.models.user import User

# from app.models.review import Review
# from app.models.activity_log import ActivityLog


# --- Collect model names for __all__ ---
__all__ = [
    "User",
    "FreelancerProfile",
    # 'Skill',
    # 'FreelancerSkill',
    # 'Project',
    # 'ProjectSkill',
    "Deliverable",
    "Feedback",
    # 'EscrowTransaction',
    # 'PortfolioItem',
    "Notification",
    # 'Review',
    # 'ActivityLog'
]
