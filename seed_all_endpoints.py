"""
UPDATED SEED FILE - WITH PORTFOLIO SUPPORT
Added: location, professional_title, avatar_url, and image deliverables
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
            'freelancer_profiles', 'projects', 'activity_logs', 'users'
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
    """Create users for testing ALL endpoints - WITH PORTFOLIO DATA"""
    print("\n👥 Creating users with portfolio data...")
    
    users_data = [
        # Admin Users - for admin endpoints
        {
            'email': 'admin@reelbrief.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_verified': True,
            'location': 'Nairobi, Kenya',
            'professional_title': 'Platform Administrator',
            'avatar_url': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400',
            'bio': 'Platform administrator ensuring smooth operations.'
        },
        
        # Client Users - for client endpoints
        {
            'email': 'sarah@techstartup.com',
            'password': 'client123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'client',
            'is_verified': True,
            'location': 'San Francisco, USA',
            'professional_title': 'Tech Startup Founder',
            'avatar_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400',
            'bio': 'Building innovative products that change the world.'
        },
        {
            'email': 'mike@creativeagency.com',
            'password': 'client123',
            'first_name': 'Mike',
            'last_name': 'Chen',
            'role': 'client',
            'is_verified': True,
            'location': 'London, UK',
            'professional_title': 'Creative Director',
            'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
            'bio': 'Leading creative campaigns for global brands.'
        },
        
        # Freelancer Users - with different statuses for testing
        {
            'email': 'alex@designer.com',
            'password': 'freelancer123',
            'first_name': 'Alex',
            'last_name': 'Thompson',
            'role': 'freelancer',
            'is_verified': True,
            'location': 'Berlin, Germany',
            'professional_title': 'Senior UI/UX Designer',
            'avatar_url': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400',
            'bio': 'Passionate UI/UX designer with 5+ years experience creating beautiful, user-centered digital experiences.',
            'profile': {
                'name': 'Alex Thompson',
                'email': 'alex@designer.com',
                'bio': 'UI/UX designer with 5+ years experience.',
                'hourly_rate': 85.00,
                'years_experience': 5,
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
            'location': 'Mumbai, India',
            'professional_title': 'Full-Stack Developer & Video Editor',
            'avatar_url': 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400',
            'bio': 'Full-stack developer specializing in React and Node.js, with a passion for video production.',
            'profile': {
                'name': 'Priya Patel',
                'email': 'priya@developer.com',
                'bio': 'Full-stack developer and video editor.',
                'hourly_rate': 95.00,
                'years_experience': 7,
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
            'location': 'Barcelona, Spain',
            'professional_title': '3D Animator & Motion Designer',
            'avatar_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400',
            'bio': '3D animator and motion graphics artist bringing ideas to life through stunning visuals.',
            'profile': {
                'name': 'Carlos Martinez',
                'email': 'carlos@animator.com',
                'bio': '3D animator and motion graphics artist.',
                'hourly_rate': 110.00,
                'years_experience': 8,
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
            'location': 'Toronto, Canada',
            'professional_title': 'Content Writer & Copywriter',
            'avatar_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400',
            'bio': 'Content writer and copywriter crafting compelling stories that convert.',
            'profile': {
                'name': 'Lisa Zhang',
                'email': 'lisa@writer.com',
                'bio': 'Content writer and copywriter.',
                'hourly_rate': 65.00,
                'years_experience': 4,
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
            'location': 'Miami, USA',
            'professional_title': 'Digital Marketing Specialist',
            'avatar_url': 'https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=400',
            'bio': 'Digital marketing expert helping brands grow their online presence.',
            'profile': {
                'name': 'Sophia Garcia',
                'email': 'sophia@marketing.com',
                'bio': 'Digital marketing expert.',
                'hourly_rate': 75.00,
                'years_experience': 6,
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
            is_active=True,
            location=user_data.get('location'),
            professional_title=user_data.get('professional_title'),
            avatar_url=user_data.get('avatar_url'),
            bio=user_data.get('bio')
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
                years_experience=profile_data.get('years_experience'),
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
        print(f"   ✅ {user.role}: {user.email} ({user.professional_title})")
    
    db.session.commit()
    return created_users

def seed_projects(users):
    """Create projects for testing project endpoints"""
    print("\n📁 Creating projects for endpoint testing...")
    
    projects_data = [
        # Active projects with different statuses for testing
        {
            'title': 'Mobile App UI/UX Redesign',
            'description': 'Complete mobile app redesign project with modern interface and improved user experience',
            'budget': 5000.00,
            'deadline': datetime.utcnow() + timedelta(days=30),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'alex@designer.com',
            'status': 'active',
            'project_type': 'UI/UX Design'
        },
        {
            'title': 'Product Launch Video',
            'description': 'Promotional video for product launch with motion graphics and professional editing',
            'budget': 8000.00,
            'deadline': datetime.utcnow() + timedelta(days=45),
            'client_email': 'mike@creativeagency.com',
            'freelancer_email': 'priya@developer.com',
            'status': 'active',
            'project_type': 'Video Production'
        },
        {
            'title': '3D Logo Animation',
            'description': 'Animated 3D logo for brand identity with multiple variations',
            'budget': 3500.00,
            'deadline': datetime.utcnow() + timedelta(days=25),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'carlos@animator.com',
            'status': 'active',
            'project_type': '3D Animation'
        },
        {
            'title': 'Website Content Writing',
            'description': 'SEO-optimized content creation for website pages',
            'budget': 2000.00,
            'deadline': datetime.utcnow() + timedelta(days=20),
            'client_email': 'mike@creativeagency.com', 
            'freelancer_email': 'lisa@writer.com',
            'status': 'active',
            'project_type': 'Content Writing'
        },
        
        # Completed projects for testing reviews and portfolios
        {
            'title': 'E-commerce Website Design',
            'description': 'Complete e-commerce website design with user-friendly interface and modern aesthetics',
            'budget': 3000.00,
            'deadline': datetime.utcnow() - timedelta(days=10),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'alex@designer.com',
            'status': 'completed',
            'completed_at': datetime.utcnow() - timedelta(days=5),
            'project_type': 'Web Design'
        },
        {
            'title': 'Social Media Campaign',
            'description': 'Comprehensive social media marketing campaign with graphics and copy',
            'budget': 4500.00,
            'deadline': datetime.utcnow() - timedelta(days=15),
            'client_email': 'mike@creativeagency.com',
            'freelancer_email': 'priya@developer.com',
            'status': 'completed',
            'completed_at': datetime.utcnow() - timedelta(days=8),
            'project_type': 'Marketing'
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
            project_type=proj_data.get('project_type'),
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

def seed_deliverables(projects_info):
    """Create deliverables with IMAGE files for portfolio cover images"""
    print("\n📦 Creating deliverables with images for portfolio...")
    
    # Sample image URLs for different project types
    sample_images = {
        'UI/UX Design': [
            'https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800',
            'https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=800',
            'https://images.unsplash.com/photo-1559028012-481c04fa702d?w=800'
        ],
        'Web Design': [
            'https://images.unsplash.com/photo-1547658719-da2b51169166?w=800',
            'https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800'
        ],
        'Video Production': [
            'https://images.unsplash.com/photo-1536240478700-b869070f9279?w=800',
            'https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=800'
        ],
        '3D Animation': [
            'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800',
            'https://images.unsplash.com/photo-1614853316476-de00d14cb1fc?w=800'
        ],
        'Content Writing': [
            'https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800',
            'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800'
        ],
        'Marketing': [
            'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800',
            'https://images.unsplash.com/photo-1533750349088-cd871a92f312?w=800'
        ]
    }
    
    deliverable_statuses = ['approved', 'pending', 'revision_requested', 'rejected']
    
    for project_info in projects_info:
        project = project_info['project']
        
        if project.freelancer_id:
            project_type = project.project_type or 'UI/UX Design'
            images = sample_images.get(project_type, sample_images['UI/UX Design'])
            
            # Create 2-3 deliverables per project with different statuses
            for i in range(1, random.randint(2, 4)):
                status = random.choice(deliverable_statuses) if project.status != 'completed' else 'approved'
                
                # Use image for first deliverable, document for others
                is_image = (i == 1 and status == 'approved')
                
                deliverable = Deliverable(
                    project_id=project.id,
                    uploaded_by=project.freelancer_id,
                    title=f'Deliverable {i} for {project.title}',
                    version_number=i,
                    file_url=random.choice(images) if is_image else f'https://example.com/project-{project.id}-v{i}.pdf',
                    file_type='image' if is_image else 'document',
                    thumbnail_url=random.choice(images) if is_image else None,
                    status=status,
                    description=f'Version {i} deliverable for {project.title}',
                    uploaded_at=datetime.utcnow() - timedelta(days=random.randint(1, 20))
                )
                
                if status in ['approved', 'revision_requested', 'rejected']:
                    deliverable.reviewed_at = deliverable.uploaded_at + timedelta(hours=24)
                    deliverable.reviewed_by = project_info['client'].id
                
                db.session.add(deliverable)
    
    db.session.commit()
    print("   ✅ Created deliverables with images for portfolio covers")

def seed_escrows(users, projects_info):
    """Create escrows for escrow endpoint testing"""
    print("\n💰 Creating escrow transactions...")
    
    admin_user = users['admin@reelbrief.com']
    
    for i, project_info in enumerate(projects_info):
        project = project_info['project']
        
        if project.freelancer_id and project.status in ['active', 'completed']:
            escrow = EscrowTransaction(
                project_id=project.id,
                client_id=project.client_id,
                freelancer_id=project.freelancer_id,
                admin_id=admin_user.id,
                amount=project.budget,
                currency="USD",
                status='released' if project.status == 'completed' else 'held',
                invoice_number=f"INV-{project.id:04d}-{random.randint(1000, 9999)}",
                invoice_url=f"https://example.com/invoices/INV-{project.id:04d}",
                payment_method="credit_card",
                held_at=project.created_at,
                notes=f"Escrow for project: {project.title}"
            )
            
            if project.status == 'completed':
                escrow.released_at = datetime.utcnow() - timedelta(days=5)
            
            db.session.add(escrow)
            print(f"   ✅ ${escrow.amount} - {escrow.status}")
    
    db.session.commit()

def seed_feedback():
    """Create feedback for feedback endpoint testing"""
    print("\n💬 Creating feedback...")
    
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
    print(f"    Created {feedback_count} feedback items")

def seed_reviews(projects_info):
    """Create reviews for review endpoint testing"""
    print("\n Creating reviews...")
    
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
    print(f"   Created {review_count} reviews")

def seed_invoices(projects_info):
    """Create invoices with different statuses"""
    print("\n Creating invoices...")
    
    invoice_statuses = ['unpaid', 'paid', 'overdue', 'cancelled']
    invoice_count = 0
    
    for i, project_info in enumerate(projects_info):
        project = project_info['project']
        
        if project.freelancer_id:
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
    print(f"    Created {invoice_count} invoices")

def seed_activity_logs(users, projects_info):
    """Create activity logs for dashboard"""
    print("\n Creating activity logs...")
    
    activities = [
        {"action": "created a new project", "resource_type": "project"},
        {"action": "submitted a deliverable", "resource_type": "deliverable"},
        {"action": "approved a deliverable", "resource_type": "deliverable"},
        {"action": "requested revision", "resource_type": "feedback"},
        {"action": "released escrow payment", "resource_type": "escrow"},
        {"action": "completed project", "resource_type": "project"},
        {"action": "left a review", "resource_type": "review"},
        {"action": "updated profile", "resource_type": "user"},
        {"action": "uploaded portfolio item", "resource_type": "portfolio"},
        {"action": "sent message", "resource_type": "message"}
    ]
    
    project_ids = [p['project'].id for p in projects_info] if projects_info else []
    
    for i in range(15):
        user = random.choice(list(users.values()))
        activity_data = random.choice(activities)
        
        activity = ActivityLog(
            user_id=user.id,
            action=activity_data["action"],
            resource_type=activity_data["resource_type"],
            resource_id=random.choice(project_ids) if project_ids else None,
            details={"note": f"Automated seed data for {activity_data['action']}"},
            created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 168))
        )
        db.session.add(activity)
    
    db.session.commit()
    print("   ✅ Created 15 activity log entries")

def print_success_message():
    """Print success message with testing guide"""
    print("\n" + "="*70)
    print("🎉 DATABASE SEEDED WITH PORTFOLIO SUPPORT!")
    print("="*70)
    
    print(f"\n FINAL COUNTS:")
    print(f"   Users: {User.query.count()}")
    print(f"   Projects: {Project.query.count()}")
    print(f"   Escrows: {EscrowTransaction.query.count()}")
    print(f"   Deliverables: {Deliverable.query.count()}")
    print(f"   Invoices: {Invoice.query.count()}")
    print(f"   Feedback: {Feedback.query.count()}")
    print(f"   Reviews: {Review.query.count()}")
    print(f"   Activities: {ActivityLog.query.count()}")
    
    print(f"\n TEST CREDENTIALS:")
    print(f"   Admin:      admin@reelbrief.com / admin123")
    print(f"   Client:     sarah@techstartup.com / client123")
    print(f"   Freelancer: alex@designer.com / freelancer123")
    print(f"   Pending:    sophia@marketing.com / freelancer123")
    
    print(f"\n PORTFOLIO FEATURES:")
    print(f"   Profile pictures (avatar_url)")
    print(f"   Professional titles")
    print(f"   Locations")
    print(f"   Image deliverables for covers")
    print(f"   2 completed projects ready for portfolios")
    
    print(f"\n READY TO TEST PORTFOLIO!")
    print("="*70)

def seed_database():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print