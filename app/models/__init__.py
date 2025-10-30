"""
app/models/__init__.py
Owner: Ryan
Description: Central model registry for the ReelBrief backend.
"""

from pathlib import Path

from app.extensions import db
from app.models.activity_log import ActivityLog

# --- Core Models ---
from app.models.user import User
from app.models.freelancer_profile import FreelancerProfile
from app.models.project import Project
from app.models.deliverable import Deliverable
from app.models.escrow_transaction import EscrowTransaction
from app.models.feedback import Feedback
from app.models.invoice import Invoice
from app.models.notification import Notification
from app.models.portfolio_item import PortfolioItem
from app.models.project import Project
from app.models.review import Review

# Optional / future imports (uncomment when ready)
# from app.models.skill import Skill, FreelancerSkill
# from app.models.project_skill import ProjectSkill
# from app.models.escrow_transaction import EscrowTransaction
# from app.models.portfolio_item import PortfolioItem
# from app.models.review import Review
# from app.models.activity_log import ActivityLog

# --- Collect model names for __all__ ---
__all__ = [
    "User",
    "FreelancerProfile",
    # 'Skill',
    # 'FreelancerSkill',
    "Project",
    # 'ProjectSkill',
    "Deliverable",
    "Feedback",
    "EscrowTransaction",
    "PortfolioItem",
    "Notification",
    "Review",
    "ActivityLog",
    "Invoice",
]
