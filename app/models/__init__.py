"""
app/models/__init__.py
Owner: Ryan
Description: Central model registry for the ReelBrief backend.
"""

from app.extensions import db

# --- Core Models ---
from app.models.user import User
from app.models.freelancer_profile import FreelancerProfile
from app.models.project import Project
from app.models.deliverable import Deliverable
from app.models.feedback import Feedback
from app.models.notification import Notification

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
    "Project",
    "Deliverable",
    "Feedback",
    "Notification",
    # "Skill",
    # "FreelancerSkill",
    # "ProjectSkill",
    # "EscrowTransaction",
    # "PortfolioItem",
    # "Review",
    # "ActivityLog",
]
