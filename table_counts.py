from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    print("📊 CURRENT DATA COUNTS:")
    print("-" * 30)
    
    try:
        from app.models.user import User
        print(f"Users: {User.query.count()}")
    except: pass
    
    try:
        from app.models.project import Project
        print(f"Projects: {Project.query.count()}")
    except: pass
    
    try:
        from app.models.deliverable import Deliverable
        print(f"Deliverables: {Deliverable.query.count()}")
    except: pass
    
    try:
        from app.models.portfolio_item import PortfolioItem
        print(f"Portfolio Items: {PortfolioItem.query.count()}")
    except: pass
    
    try:
        from app.models.freelancer_profile import FreelancerProfile
        print(f"Freelancer Profiles: {FreelancerProfile.query.count()}")
    except: pass
    
    try:
        from app.models.skill import Skill
        print(f"Skills: {Skill.query.count()}")
    except: pass
    
    try:
        from app.models.review import Review
        print(f"Reviews: {Review.query.count()}")
    except: pass
    
    try:
        from app.models.feedback import Feedback
        print(f"Feedback: {Feedback.query.count()}")
    except: pass

