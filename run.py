from app import create_app
from app.extensions import db
from app.models import *  # Import all models for migrations

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make database and models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'FreelancerProfile': FreelancerProfile,
        'Skill': Skill,
        'Project': Project,
        'Deliverable': Deliverable,
        'Feedback': Feedback,
        'EscrowTransaction': EscrowTransaction,
        'PortfolioItem': PortfolioItem,
        'Notification': Notification,
        'Review': Review,
        'ActivityLog': ActivityLog
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)

