"""
Models package - hybrid auto-import and explicit registration.
---------------------------------------------------------------
Explicit imports ensure Flask-Migrate detects models.
Auto-import safely loads any new model files teammates add.
"""

import importlib
import pkgutil
from pathlib import Path

# --- Explicit imports (required for Flask-Migrate) ---
# from app.models.user import User
# from app.models.freelancer_profile import FreelancerProfile
# from app.models.skill import Skill, FreelancerSkill
# from app.models.project import Project, ProjectSkill
# from app.models.deliverable import Deliverable
# from app.models.feedback import Feedback
# from app.models.escrow_transaction import EscrowTransaction
# from app.models.portfolio_item import PortfolioItem
# from app.models.notification import Notification
# from app.models.review import Review
# from app.models.activity_log import ActivityLog


# --- Auto-import any new modules teammates add ---
# This prevents forgetting to import new models manually.
package_name = __name__  # "app.models"
package_path = Path(__file__).parent

for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
    if not is_pkg and module_name != "__init__":
        full_module_name = f"{package_name}.{module_name}"
        if full_module_name not in globals():
            try:
                importlib.import_module(full_module_name)
            except ImportError as e:
                print(f"[models] Skipped {module_name}: {e}")


# --- Collect model names for __all__ ---
__all__ = [
    # 'User',
    # 'FreelancerProfile',
    # 'Skill',
    # 'FreelancerSkill',
    # 'Project',
    # 'ProjectSkill',
    # 'Deliverable',
    # 'Feedback',
    # 'EscrowTransaction',
    # 'PortfolioItem',
    # 'Notification',
    # 'Review',
    # 'ActivityLog'
]
