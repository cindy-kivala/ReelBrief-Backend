"""
FINAL WORKING SEED FILE - FIXED DECIMAL MULTIPLICATION
"""

from app import create_app, db
from app.models import (
    User, Project, Deliverable, Feedback, FreelancerProfile, 
    Invoice, Review, ActivityLog, EscrowTransaction, Skill, FreelancerSkill
)
from datetime import datetime, timedelta
from sqlalchemy import text
import random
from decimal import Decimal

def clear_existing_data():
    """Completely clear all existing data"""
    print("🗑️  Clearing ALL existing data...")
    try:
        # Clear all tables in correct order to handle foreign keys
        tables = [
            'feedback', 'reviews', 'invoices', 'notifications',
            'deliverables', 'escrow_transactions', 'portfolio_items',
            'project_skills', 'freelancer_skills', 'skills',
            'freelancer_profiles', 'projects', 'activity_log', 'users'
        ]
        
        for table in tables:
            db.session.execute(text(f"DELETE FROM {table} CASCADE"))
        
        db.session.commit()
        print("✅ All existing data cleared successfully")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error clearing: {e}")
        raise

def seed_skills():
    """Create skills for freelancers"""
    print("\n🛠️  Creating skills...")
    
    skills_data = [
        'UI/UX Design', 'Figma', 'Sketch', 'Adobe XD', 'Prototyping', 'User Research',
        'React', 'Node.js', 'Python', 'Video Editing', 'Motion Graphics', 'JavaScript',
        'Blender', 'Cinema 4D', 'After Effects', '3D Animation',
        'Content Writing', 'SEO', 'Marketing Copy', 'Technical Writing', 'Copywriting',
        'Social Media Marketing', 'Analytics', 'Campaign Management',
        'Web Development', 'Mobile Development', 'Graphic Design', 'Illustration'
    ]
    
    created_skills = {}
    
    for skill_name in skills_data:
        skill = Skill(name=skill_name)
        db.session.add(skill)
        created_skills[skill_name] = skill
        print(f"   ✅ {skill_name}")
    
    db.session.commit()
    return created_skills

def seed_users(skills):
    """Create users for testing ALL endpoints"""
    print("\n👥 Creating users for all endpoint testing...")
    
    users_data = [
        # Admin Users - for admin endpoints
        {
            'email': 'admin@reelbrief.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_verified': True
        },
        
        # Client Users - for client endpoints
        {
            'email': 'sarah@techstartup.com',
            'password': 'client123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'client',
            'is_verified': True
        },
        {
            'email': 'mike@creativeagency.com',
            'password': 'client123',
            'first_name': 'Mike',
            'last_name': 'Chen',
            'role': 'client',
            'is_verified': True
        },
        
        # Freelancer Users - with different statuses for testing
        {
            'email': 'alex@designer.com',
            'password': 'freelancer123',
            'first_name': 'Alex',
            'last_name': 'Thompson',
            'role': 'freelancer',
            'is_verified': True,
            'profile': {
                'name': 'Alex Thompson',
                'email': 'alex@designer.com',
                'bio': 'UI/UX designer with 5+ years experience.',
                'hourly_rate': 85.00,
                'portfolio_url': 'https://alexthompson.design',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['UI/UX Design', 'Figma', 'Prototyping', 'User Research']
            }
        },
        {
            'email': 'priya@developer.com',
            'password': 'freelancer123',
            'first_name': 'Priya',
            'last_name': 'Patel',
            'role': 'freelancer',
            'is_verified': True,
            'profile': {
                'name': 'Priya Patel',
                'email': 'priya@developer.com',
                'bio': 'Full-stack developer and video editor.',
                'hourly_rate': 95.00,
                'portfolio_url': 'https://priyapatel.dev',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['React', 'Node.js', 'Python', 'Video Editing']
            }
        },
        {
            'email': 'carlos@animator.com',
            'password': 'freelancer123',
            'first_name': 'Carlos',
            'last_name': 'Martinez',
            'role': 'freelancer',
            'is_verified': True,
            'profile': {
                'name': 'Carlos Martinez',
                'email': 'carlos@animator.com',
                'bio': '3D animator and motion graphics artist.',
                'hourly_rate': 110.00,
                'portfolio_url': 'https://carlosanimation.com',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['Blender', 'Cinema 4D', 'After Effects', '3D Animation']
            }
        },
        {
            'email': 'lisa@writer.com',
            'password': 'freelancer123',
            'first_name': 'Lisa',
            'last_name': 'Zhang',
            'role': 'freelancer',
            'is_verified': True,
            'profile': {
                'name': 'Lisa Zhang',
                'email': 'lisa@writer.com',
                'bio': 'Content writer and copywriter.',
                'hourly_rate': 65.00,
                'portfolio_url': 'https://lisazhangwriting.com',
                'open_to_work': False,  # For testing availability toggle
                'application_status': 'approved',
                'skills': ['Content Writing', 'SEO', 'Marketing Copy', 'Technical Writing']
            }
        },
        {
            'email': 'sophia@marketing.com', 
            'password': 'freelancer123',
            'first_name': 'Sophia',
            'last_name': 'Garcia',
            'role': 'freelancer',
            'is_verified': True,
            'profile': {
                'name': 'Sophia Garcia',
                'email': 'sophia@marketing.com',
                'bio': 'Digital marketing expert.',
                'hourly_rate': 75.00,
                'portfolio_url': 'https://sophiamarketing.com',
                'open_to_work': True,
                'application_status': 'pending',  # For testing approval endpoints
                'skills': ['Social Media Marketing', 'SEO', 'Analytics']
            }
        }
    ]
    
    created_users = {}
    
    for user_data in users_data:
        user = User(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            is_verified=user_data['is_verified'],
            is_active=True
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.flush()
        
        if 'profile' in user_data:
            profile_data = user_data['profile']
            profile = FreelancerProfile(
                user_id=user.id,
                name=profile_data['name'],
                email=profile_data['email'],
                bio=profile_data['bio'],
                hourly_rate=profile_data['hourly_rate'],
                portfolio_url=profile_data['portfolio_url'],
                open_to_work=profile_data['open_to_work'],
                application_status=profile_data['application_status']
            )
            
            if profile_data['application_status'] == 'approved':
                profile.approved_at = datetime.utcnow()
                # Use the admin user ID for approval
                admin_user = User.query.filter_by(email='admin@reelbrief.com').first()
                if admin_user:
                    profile.approved_by = admin_user.id
            
            db.session.add(profile)
            db.session.flush()
            
            # Add skills to freelancer profile
            for skill_name in profile_data['skills']:
                if skill_name in skills:
                    freelancer_skill = FreelancerSkill(
                        freelancer_id=profile.id,
                        skill_id=skills[skill_name].id,
                        proficiency=random.choice(['beginner', 'intermediate', 'expert'])
                    )
                    db.session.add(freelancer_skill)
        
        created_users[user_data['email']] = user
        print(f"   ✅ {user.role}: {user.email}")
    
    db.session.commit()
    return created_users

def seed_projects(users):
    """Create projects for testing project endpoints"""
    print("\n📁 Creating projects for endpoint testing...")
    
    projects_data = [
        # Active projects with different statuses for testing
        {
            'title': 'Mobile App UI/UX Redesign',
            'description': 'Complete mobile app redesign project',
            'budget': 5000.00,
            'deadline': datetime.utcnow() + timedelta(days=30),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'alex@designer.com',
            'status': 'active'
        },
        {
            'title': 'Product Launch Video',
            'description': 'Promotional video for product launch',
            'budget': 8000.00,
            'deadline': datetime.utcnow() + timedelta(days=45),
            'client_email': 'mike@creativeagency.com',
            'freelancer_email': 'priya@developer.com',
            'status': 'active'
        },
        {
            'title': '3D Logo Animation',
            'description': 'Animated logo for brand identity',
            'budget': 3500.00,
            'deadline': datetime.utcnow() + timedelta(days=25),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'carlos@animator.com',
            'status': 'active'
        },
        {
            'title': 'Website Content Writing',
            'description': 'Content creation for website',
            'budget': 2000.00,
            'deadline': datetime.utcnow() + timedelta(days=20),
            'client_email': 'mike@creativeagency.com', 
            'freelancer_email': 'lisa@writer.com',
            'status': 'active'
        },
        
        # Completed projects for testing reviews and completion
        {
            'title': 'Completed Web Design',
            'description': 'Website design completed successfully',
            'budget': 3000.00,
            'deadline': datetime.utcnow() - timedelta(days=10),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'alex@designer.com',
            'status': 'completed',
            'completed_at': datetime.utcnow() - timedelta(days=5)
        },
        {
            'title': 'Social Media Campaign',
            'description': 'Social media marketing campaign',
            'budget': 4500.00,
            'deadline': datetime.utcnow() - timedelta(days=15),
            'client_email': 'mike@creativeagency.com',
            'freelancer_email': 'priya@developer.com',
            'status': 'completed',
            'completed_at': datetime.utcnow() - timedelta(days=8)
        }
    ]
    
    created_projects = []
    
    for proj_data in projects_data:
        project = Project(
            title=proj_data['title'],
            description=proj_data['description'],
            budget=proj_data['budget'],
            deadline=proj_data['deadline'],
            status=proj_data['status'],
            created_at=datetime.utcnow() - timedelta(days=random.randint(5, 60))
        )
        
        project.client_id = users[proj_data['client_email']].id
        
        if 'freelancer_email' in proj_data:
            project.freelancer_id = users[proj_data['freelancer_email']].id
        
        if proj_data['status'] == 'completed':
            project.completed_at = proj_data.get('completed_at')
        
        db.session.add(project)
        db.session.flush()
        
        project_info = {
            'project': project,
            'client': users[proj_data['client_email']],
            'freelancer': users[proj_data['freelancer_email']] if 'freelancer_email' in proj_data else None
        }
        
        created_projects.append(project_info)
        print(f"   ✅ {project.status}: {project.title}")
    
    db.session.commit()
    return created_projects

def seed_escrows(users, projects_info):
    """Create escrows for escrow endpoint testing"""
    print("\n💰 Creating escrow transactions for endpoint testing...")
    
    admin_user = users['admin@reelbrief.com']
    
    for i, project_info in enumerate(projects_info):
        project = project_info['project']
        
        if project.freelancer_id and project.status in ['active', 'completed']:
            escrow = EscrowTransaction(
                project_id=project.id,
                client_id=project.client_id,
                freelancer_id=project.freelancer_id,
                admin_id=admin_user.id,  # Required field
                amount=project.budget,
                currency="USD",
                status='released' if project.status == 'completed' else 'held',
                invoice_number=f"INV-{project.id:04d}-{random.randint(1000, 9999)}",  # Required field
                invoice_url=f"https://example.com/invoices/INV-{project.id:04d}",
                payment_method="credit_card",
                held_at=project.created_at,  # Use held_at instead of created_at
                notes=f"Escrow for project: {project.title}"
            )
            
            if project.status == 'completed':
                escrow.released_at = datetime.utcnow() - timedelta(days=5)
            
            db.session.add(escrow)
            print(f"   ✅ ${escrow.amount} - {escrow.status}")
    
    db.session.commit()

def seed_deliverables(projects_info):
    """Create deliverables with different statuses for testing"""
    print("\n📦 Creating deliverables for endpoint testing...")
    
    deliverable_statuses = ['approved', 'pending', 'revision_requested', 'rejected']
    
    for project_info in projects_info:
        project = project_info['project']
        
        if project.freelancer_id:
            # Create 2-3 deliverables per project with different statuses
            for i in range(1, random.randint(2, 4)):
                status = random.choice(deliverable_statuses)
                
                deliverable = Deliverable(
                    project_id=project.id,
                    uploaded_by=project.freelancer_id,
                    title=f'Deliverable {i} for {project.title}',
                    version_number=i,
                    file_url=f'https://example.com/project-{project.id}-v{i}.pdf',
                    file_type='document',
                    status=status,
                    description=f'Version {i} deliverable for {project.title}',
                    uploaded_at=datetime.utcnow() - timedelta(days=random.randint(1, 20))
                )
                
                if status in ['approved', 'revision_requested', 'rejected']:
                    deliverable.reviewed_at = deliverable.uploaded_at + timedelta(hours=24)
                    deliverable.reviewed_by = project_info['client'].id
                
                db.session.add(deliverable)
    
    db.session.commit()
    print("   ✅ Created deliverables with various statuses")

def seed_feedback():
    """Create feedback for feedback endpoint testing"""
    print("\n💬 Creating feedback for endpoint testing...")
    
    deliverables = Deliverable.query.all()
    feedback_messages = [
        "This looks great! Can we make the colors more vibrant?",
        "The design is clean but needs better spacing.",
        "Excellent work! Just a few minor adjustments needed.",
        "The video pacing is perfect but audio needs improvement.",
        "Content is well-written but needs SEO optimization.",
        "Animation is smooth but timing could be better."
    ]
    
    feedback_count = 0
    for deliverable in deliverables:
        if deliverable.status in ['revision_requested', 'rejected']:
            # Create feedback that needs resolution
            feedback = Feedback(
                deliverable_id=deliverable.id,
                user_id=deliverable.project.client_id,
                feedback_type='revision',
                content=random.choice(feedback_messages),
                priority=random.choice(['low', 'medium', 'high']),
                is_resolved=False,
                created_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(feedback)
            feedback_count += 1
    
    db.session.commit()
    print(f"   ✅ Created {feedback_count} feedback items")

def seed_reviews(projects_info):
    """Create reviews for review endpoint testing"""
    print("\n⭐ Creating reviews for endpoint testing...")
    
    review_comments = [
        "Excellent work! Very professional and delivered on time.",
        "Great communication and quality work. Highly recommended!",
        "Good work but had some delays in communication.",
        "Outstanding quality and attention to detail.",
        "Reliable freelancer who understands requirements well."
    ]
    
    review_count = 0
    for project_info in projects_info:
        project = project_info['project']
        
        if project.status == 'completed' and project.freelancer_id:
            # Client reviews freelancer
            review = Review(
                project_id=project.id,
                client_id=project.client_id,
                freelancer_id=project.freelancer_id,
                rating=random.randint(4, 5),
                review_text=random.choice(review_comments),
                created_at=project.completed_at + timedelta(days=1)
            )
            db.session.add(review)
            review_count += 1
    
    db.session.commit()
    print(f"   ✅ Created {review_count} reviews")

def seed_invoices(projects_info):
    """Create invoices with different statuses for testing"""
    print("\n🧾 Creating invoices for endpoint testing...")
    
    invoice_statuses = ['unpaid', 'paid', 'overdue', 'cancelled']
    invoice_count = 0
    
    for i, project_info in enumerate(projects_info):
        project = project_info['project']
        
        if project.freelancer_id:
            # Convert Decimal to float for multiplication, then back to Decimal
            budget_float = float(project.budget)
            invoice_amount = Decimal(str(budget_float * random.uniform(0.3, 0.8)))
            
            invoice = Invoice(
                project_id=project.id,
                client_id=project.client_id,
                freelancer_id=project.freelancer_id,
                invoice_number=f"INV-{project.id:04d}-{random.randint(1000, 9999)}",
                amount=invoice_amount,
                currency="USD",
                issue_date=datetime.utcnow() - timedelta(days=random.randint(1, 15)),
                due_date=datetime.utcnow() + timedelta(days=30 if i % 2 == 0 else -5),
                status=invoice_statuses[i % len(invoice_statuses)],
                pdf_url=f"https://example.com/invoices/INV-{project.id:04d}.pdf",
                notes=f"Invoice for {project.title}"
            )
            
            if invoice.status == 'paid':
                invoice.paid_at = datetime.utcnow() - timedelta(days=2)
            
            db.session.add(invoice)
            invoice_count += 1
    
    db.session.commit()
    print(f"   ✅ Created {invoice_count} invoices")

def seed_activity_logs(users, projects_info):
    """Create activity logs for dashboard testing"""
    print("\n📊 Creating activity logs for dashboard...")
    
    activities = [
        "created a new project",
        "submitted a deliverable", 
        "approved a deliverable",
        "requested revision",
        "released escrow payment",
        "completed project",
        "left a review"
    ]
    
    for i in range(15):  # Create 15 activity entries
        user = random.choice(list(users.values()))
        activity = ActivityLog(
            user_id=user.id,
            action=random.choice(activities),
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 168))
        )
        db.session.add(activity)
    
    db.session.commit()
    print("   ✅ Created activity log entries")

def print_success_message():
    """Print success message with testing guide"""
    print("\n" + "="*70)
    print("🎉 COMPREHENSIVE ENDPOINT TESTING DATABASE READY!")
    print("="*70)
    
    print(f"\n📊 FINAL COUNTS:")
    print(f"   👥 Users: {User.query.count()}")
    print(f"   📁 Projects: {Project.query.count()}")
    print(f"   💰 Escrows: {EscrowTransaction.query.count()}")
    print(f"   📦 Deliverables: {Deliverable.query.count()}")
    print(f"   🧾 Invoices: {Invoice.query.count()}")
    print(f"   💬 Feedback: {Feedback.query.count()}")
    print(f"   ⭐ Reviews: {Review.query.count()}")
    print(f"   📊 Activities: {ActivityLog.query.count()}")
    
    print(f"\n🔑 TEST CREDENTIALS:")
    print(f"   Admin:     admin@reelbrief.com / admin123")
    print(f"   Client:    sarah@techstartup.com / client123")
    print(f"   Freelancer: alex@designer.com / freelancer123")
    print(f"   Pending:   sophia@marketing.com / freelancer123")
    
    print(f"\n🚀 READY TO TEST ALL ENDPOINTS!")
    print("="*70)

def seed_database():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print("🌱 SEEDING COMPLETE DATABASE FOR ALL ENDPOINT TESTING")
        print("="*70)
        
        try:
            clear_existing_data()
            skills = seed_skills()
            users = seed_users(skills)
            projects_info = seed_projects(users)
            seed_escrows(users, projects_info)  # Pass users to get admin_id
            seed_deliverables(projects_info)
            seed_feedback()
            seed_reviews(projects_info)
            seed_invoices(projects_info)
            seed_activity_logs(users, projects_info)
            
            print_success_message()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    seed_database()