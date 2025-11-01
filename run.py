from app import create_app
from app.extensions import db
# from app.models import *  # Import all models for migrations
from app.models.user import User
from app.models.deliverable import Deliverable
from app.models.feedback import Feedback


# from app.models.project import Project
# from app.models.freelancer_profile import FreelancerProfile
# from app.models.skill import Skill
# from app.models.escrow_transaction import EscrowTransaction
# from app.models.portfolio_item import PortfolioItem
# from app.models.notification import Notification
# from app.models.review import Review
# from app.models.activity_log import ActivityLog

app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Make database and models available in Flask shell"""
    return {
        "db": db,
        "User": User,
        # "FreelancerProfile": FreelancerProfile,
        # "Skill": Skill,
        # "Project": Project,
        "Deliverable": Deliverable,
        "Feedback": Feedback,
        # "EscrowTransaction": EscrowTransaction,
        # "PortfolioItem": PortfolioItem,
        # "Notification": Notification,
        # "Review": Review,
        # "ActivityLog": ActivityLog,
    }


if __name__ == "__main__":
    app.run(debug=True, port=5000)
