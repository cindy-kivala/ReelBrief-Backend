from app import create_app

app = create_app()

with app.app_context():
    models_to_check = [
        'User', 'Project', 'ProjectSkill', 'Deliverable', 'FreelancerProfile',
        'EscrowTransaction', 'PortfolioItem', 'Review', 'Feedback', 
        'ActivityLog', 'Message', 'Invoice', 'Skill', 'Wallet', 'WalletTransaction',
        'Notification'
    ]
    
    print("🔍 Checking model imports...")
    for model_name in models_to_check:
        try:
            if model_name == 'User':
                from app.models.user import User
            elif model_name == 'Project' or model_name == 'ProjectSkill':
                from app.models.project import Project, ProjectSkill
            elif model_name == 'Deliverable':
                from app.models.deliverable import Deliverable
            elif model_name == 'FreelancerProfile':
                from app.models.freelancer_profile import FreelancerProfile
            elif model_name == 'EscrowTransaction':
                from app.models.escrow import EscrowTransaction
            elif model_name == 'PortfolioItem':
                from app.models.portfolio import PortfolioItem
            elif model_name == 'Review':
                from app.models.review import Review
            elif model_name == 'Feedback':
                from app.models.feedback import Feedback
            elif model_name == 'ActivityLog':
                from app.models.activity_log import ActivityLog
            elif model_name == 'Message':
                from app.models.message import Message
            elif model_name == 'Invoice':
                from app.models.invoice import Invoice
            elif model_name == 'Skill':
                from app.models.skill import Skill
            elif model_name == 'Wallet':
                from app.models.wallet import Wallet
            elif model_name == 'WalletTransaction':
                from app.models.wallet import WalletTransaction
            elif model_name == 'Notification':
                from app.models.notification import Notification
                
            print(f"✅ {model_name}")
        except Exception as e:
            print(f"❌ {model_name}: {e}")

    print("\n📋 Model check complete!")
