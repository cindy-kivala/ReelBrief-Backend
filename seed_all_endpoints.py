"""
COMPREHENSIVE SEED FILE - MATCHING 110 BACKEND ENDPOINTS + FRONTEND API FLOW
Maintains same user count (19 users) and conventions
"""

from app import create_app, db
from app.models import (
    User, Project, Deliverable, Feedback, FreelancerProfile, 
    Invoice, Review, ActivityLog, EscrowTransaction, Skill, FreelancerSkill, ProjectSkill,
    PortfolioItem, Notification, Wallet, WalletTransaction
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
            'wallet_transactions', 'wallets', 'notifications', 'feedback', 
            'reviews', 'invoices', 'deliverables', 'escrow_transactions', 
            'portfolio_items', 'project_skills', 'freelancer_skills', 'skills',
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
        'Web Development', 'Mobile Development', 'Graphic Design', 'Illustration',
        'Swift', 'Kotlin', 'Flutter', 'React Native', 'Vue.js', 'Angular',
        'PHP', 'Laravel', 'Django', 'Flask', 'PostgreSQL', 'MongoDB',
        'AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Git', 'Agile Methodology',
        'Photoshop', 'Illustrator', 'InDesign', 'Premiere Pro', 'Final Cut Pro',
        'WordPress', 'Shopify', 'Webflow', 'Squarespace', 'Email Marketing'
    ]
    
    created_skills = {}
    
    for skill_name in skills_data:
        skill = Skill(name=skill_name)
        db.session.add(skill)
        created_skills[skill_name] = skill
        print(f"   ✅ {skill_name}")
    
    db.session.commit()
    return created_skills

def seed_users():
    """Create 19 users matching your existing count and conventions"""
    print("\n👥 Creating 19 users (maintaining your count)...")
    
    users_data = [
        # Admin Users (1)
        {
            'email': 'admin@reelbrief.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'is_verified': True,
            'bio': 'Platform administrator ensuring smooth operations.'
        },
        
        # Client Users (6 - matching your count)
        {
            'email': 'sarah@techstartup.com',
            'password': 'client123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'client',
            'is_verified': True,
            'bio': 'Building innovative products that change the world.'
        },
        {
            'email': 'mike@creativeagency.com',
            'password': 'client123',
            'first_name': 'Mike',
            'last_name': 'Chen',
            'role': 'client',
            'is_verified': True,
            'bio': 'Leading creative campaigns for global brands.'
        },
        {
            'email': 'emma@fashionbrand.com',
            'password': 'client123',
            'first_name': 'Emma',
            'last_name': 'Rodriguez',
            'role': 'client',
            'is_verified': True,
            'bio': 'Managing fashion brand digital presence and campaigns.'
        },
        {
            'email': 'david@healthtech.com',
            'password': 'client123',
            'first_name': 'David',
            'last_name': 'Kim',
            'role': 'client',
            'is_verified': True,
            'bio': 'Leading healthcare technology innovations.'
        },
        {
            'email': 'lisa@edtech.org',
            'password': 'client123',
            'first_name': 'Lisa',
            'last_name': 'Wang',
            'role': 'client',
            'is_verified': True,
            'bio': 'Transforming education through technology.'
        },
        {
            'email': 'james@fintech.io',
            'password': 'client123',
            'first_name': 'James',
            'last_name': 'Anderson',
            'role': 'client',
            'is_verified': True,
            'bio': 'Driving financial technology innovation.'
        },
        
        # Freelancer Users (12 - matching your count)
        {
            'email': 'alex@designer.com',
            'password': 'freelancer123',
            'first_name': 'Alex',
            'last_name': 'Thompson',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Passionate UI/UX designer with 5+ years experience creating beautiful, user-centered digital experiences.',
            'profile': {
                'name': 'Alex Thompson',
                'email': 'alex@designer.com',
                'bio': 'UI/UX designer with 5+ years experience creating beautiful and functional digital products.',
                'hourly_rate': 85.00,
                'years_experience': 5,
                'portfolio_url': 'https://alexthompson.design',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['UI/UX Design', 'Figma', 'Prototyping', 'User Research', 'Web Design']
            }
        },
        {
            'email': 'priya@developer.com',
            'password': 'freelancer123',
            'first_name': 'Priya',
            'last_name': 'Patel',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Full-stack developer specializing in React and Node.js, with a passion for video production.',
            'profile': {
                'name': 'Priya Patel',
                'email': 'priya@developer.com',
                'bio': 'Full-stack developer specializing in React, Node.js, and Python with video editing skills.',
                'hourly_rate': 95.00,
                'years_experience': 7,
                'portfolio_url': 'https://priyapatel.dev',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['React', 'Node.js', 'Python', 'Video Editing', 'JavaScript', 'MongoDB']
            }
        },
        {
            'email': 'carlos@animator.com',
            'password': 'freelancer123',
            'first_name': 'Carlos',
            'last_name': 'Martinez',
            'role': 'freelancer',
            'is_verified': True,
            'bio': '3D animator and motion graphics artist bringing ideas to life through stunning visuals.',
            'profile': {
                'name': 'Carlos Martinez',
                'email': 'carlos@animator.com',
                'bio': '3D animator and motion graphics artist with expertise in Blender and Cinema 4D.',
                'hourly_rate': 110.00,
                'years_experience': 8,
                'portfolio_url': 'https://carlosanimation.com',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['Blender', 'Cinema 4D', 'After Effects', '3D Animation', 'Motion Graphics']
            }
        },
        {
            'email': 'lisa@writer.com',
            'password': 'freelancer123',
            'first_name': 'Lisa',
            'last_name': 'Zhang',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Content writer and copywriter crafting compelling stories that convert.',
            'profile': {
                'name': 'Lisa Zhang',
                'email': 'lisa@writer.com',
                'bio': 'Content writer and copywriter specializing in tech and marketing content.',
                'hourly_rate': 65.00,
                'years_experience': 4,
                'portfolio_url': 'https://lisazhangwriting.com',
                'open_to_work': False,
                'application_status': 'approved',
                'skills': ['Content Writing', 'SEO', 'Marketing Copy', 'Technical Writing', 'Copywriting']
            }
        },
        {
            'email': 'sophia@marketing.com', 
            'password': 'freelancer123',
            'first_name': 'Sophia',
            'last_name': 'Garcia',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Digital marketing expert helping brands grow their online presence.',
            'profile': {
                'name': 'Sophia Garcia',
                'email': 'sophia@marketing.com',
                'bio': 'Digital marketing expert with focus on social media and analytics.',
                'hourly_rate': 75.00,
                'years_experience': 6,
                'portfolio_url': 'https://sophiamarketing.com',
                'open_to_work': True,
                'application_status': 'pending',
                'skills': ['Social Media Marketing', 'SEO', 'Analytics', 'Campaign Management']
            }
        },
        {
            'email': 'marcus@mobile.dev',
            'password': 'freelancer123',
            'first_name': 'Marcus',
            'last_name': 'Johnson',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Mobile app developer specializing in React Native and Flutter cross-platform solutions.',
            'profile': {
                'name': 'Marcus Johnson',
                'email': 'marcus@mobile.dev',
                'bio': 'Mobile app developer specializing in React Native and Flutter cross-platform solutions.',
                'hourly_rate': 90.00,
                'years_experience': 5,
                'portfolio_url': 'https://marcusmobile.dev',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['React Native', 'Flutter', 'Mobile Development', 'JavaScript', 'Firebase']
            }
        },
        {
            'email': 'natalie@graphics.com',
            'password': 'freelancer123',
            'first_name': 'Natalie',
            'last_name': 'Chen',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Graphic designer and illustrator with a passion for branding and visual identity.',
            'profile': {
                'name': 'Natalie Chen',
                'email': 'natalie@graphics.com',
                'bio': 'Graphic designer and illustrator with a passion for branding and visual identity.',
                'hourly_rate': 70.00,
                'years_experience': 4,
                'portfolio_url': 'https://nataliechen.design',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['Graphic Design', 'Illustration', 'Photoshop', 'Illustrator', 'Branding']
            }
        },
        {
            'email': 'ryan@videopro.com',
            'password': 'freelancer123',
            'first_name': 'Ryan',
            'last_name': 'O\'Connor',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Professional video editor and filmmaker with expertise in Premiere Pro and After Effects.',
            'profile': {
                'name': 'Ryan O\'Connor',
                'email': 'ryan@videopro.com',
                'bio': 'Professional video editor and filmmaker with expertise in Premiere Pro and After Effects.',
                'hourly_rate': 85.00,
                'years_experience': 6,
                'portfolio_url': 'https://ryanoconnorfilms.com',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['Video Editing', 'After Effects', 'Premiere Pro', 'Motion Graphics', 'Color Grading']
            }
        },
        {
            'email': 'taylor@fullstack.io',
            'password': 'freelancer123',
            'first_name': 'Taylor',
            'last_name': 'Brown',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Full-stack developer with expertise in modern web technologies and cloud infrastructure.',
            'profile': {
                'name': 'Taylor Brown',
                'email': 'taylor@fullstack.io',
                'bio': 'Full-stack developer with expertise in modern web technologies and cloud infrastructure.',
                'hourly_rate': 100.00,
                'years_experience': 7,
                'portfolio_url': 'https://taylorbrown.dev',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['React', 'Node.js', 'Python', 'AWS', 'Docker', 'PostgreSQL']
            }
        },
        {
            'email': 'isabella@content.co',
            'password': 'freelancer123',
            'first_name': 'Isabella',
            'last_name': 'Rossi',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'Content strategist and SEO specialist helping brands improve their online presence.',
            'profile': {
                'name': 'Isabella Rossi',
                'email': 'isabella@content.co',
                'bio': 'Content strategist and SEO specialist helping brands improve their online presence.',
                'hourly_rate': 60.00,
                'years_experience': 5,
                'portfolio_url': 'https://isabellarossi.com',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['Content Writing', 'SEO', 'Content Strategy', 'Email Marketing', 'WordPress']
            }
        },
        {
            'email': 'kevin@devops.tech',
            'password': 'freelancer123',
            'first_name': 'Kevin',
            'last_name': 'Nguyen',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'DevOps engineer specializing in cloud infrastructure, CI/CD, and system architecture.',
            'profile': {
                'name': 'Kevin Nguyen',
                'email': 'kevin@devops.tech',
                'bio': 'DevOps engineer specializing in cloud infrastructure, CI/CD, and system architecture.',
                'hourly_rate': 120.00,
                'years_experience': 8,
                'portfolio_url': 'https://kevinnguyen.tech',
                'open_to_work': False,
                'application_status': 'approved',
                'skills': ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Linux', 'Python']
            }
        },
        {
            'email': 'olivia@uiux.design',
            'password': 'freelancer123',
            'first_name': 'Olivia',
            'last_name': 'Park',
            'role': 'freelancer',
            'is_verified': True,
            'bio': 'UI/UX designer focused on creating intuitive and accessible digital experiences.',
            'profile': {
                'name': 'Olivia Park',
                'email': 'olivia@uiux.design',
                'bio': 'UI/UX designer focused on creating intuitive and accessible digital experiences.',
                'hourly_rate': 80.00,
                'years_experience': 4,
                'portfolio_url': 'https://oliviapark.design',
                'open_to_work': True,
                'application_status': 'approved',
                'skills': ['UI/UX Design', 'Figma', 'Adobe XD', 'User Research', 'Prototyping']
            }
        }
    ]
    
    created_users = {}
    skills = {skill.name: skill for skill in Skill.query.all()}
    
    for user_data in users_data:
        # Only include fields that exist in your User model
        user = User(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            is_verified=user_data['is_verified'],
            is_active=True,
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
                years_experience=profile_data.get('years_experience', 3),
                portfolio_url=profile_data['portfolio_url'],
                open_to_work=profile_data['open_to_work'],
                application_status=profile_data['application_status']
            )
            
            if profile_data['application_status'] == 'approved':
                profile.approved_at = datetime.utcnow()
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
    """Create 10 projects matching your existing count"""
    print("\n📁 Creating 10 projects...")
    
    admin_user = users['admin@reelbrief.com']
    skills = {skill.name: skill for skill in Skill.query.all()}
    
    projects_data = [
        # Active projects (6)
        {
            'title': 'Mobile App UI/UX Redesign',
            'description': 'Complete mobile app redesign with modern interface and improved user experience',
            'budget': 5000.00,
            'deadline': datetime.utcnow() + timedelta(days=30),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'alex@designer.com',
            'status': 'active',
            'project_type': 'UI/UX Design',
            'skills': ['UI/UX Design', 'Figma', 'Prototyping']
        },
        {
            'title': 'Product Launch Video',
            'description': 'Promotional video for product launch with motion graphics and professional editing',
            'budget': 8000.00,
            'deadline': datetime.utcnow() + timedelta(days=45),
            'client_email': 'mike@creativeagency.com',
            'freelancer_email': 'priya@developer.com',
            'status': 'active',
            'project_type': 'Video Production',
            'skills': ['Video Editing', 'After Effects', 'Motion Graphics']
        },
        {
            'title': '3D Logo Animation',
            'description': 'Animated 3D logo for brand identity with multiple variations',
            'budget': 3500.00,
            'deadline': datetime.utcnow() + timedelta(days=25),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'carlos@animator.com',
            'status': 'active',
            'project_type': '3D Animation',
            'skills': ['Blender', '3D Animation', 'Cinema 4D']
        },
        {
            'title': 'Website Content Writing',
            'description': 'SEO-optimized content creation for website pages',
            'budget': 2000.00,
            'deadline': datetime.utcnow() + timedelta(days=20),
            'client_email': 'mike@creativeagency.com', 
            'freelancer_email': 'lisa@writer.com',
            'status': 'active',
            'project_type': 'Content Writing',
            'skills': ['Content Writing', 'SEO', 'Copywriting']
        },
        {
            'title': 'E-commerce Mobile App',
            'description': 'Cross-platform e-commerce mobile application development',
            'budget': 12000.00,
            'deadline': datetime.utcnow() + timedelta(days=60),
            'client_email': 'emma@fashionbrand.com',
            'freelancer_email': 'marcus@mobile.dev',
            'status': 'active',
            'project_type': 'Mobile Development',
            'skills': ['React Native', 'Mobile Development', 'JavaScript']
        },
        {
            'title': 'Brand Identity Design',
            'description': 'Complete brand identity including logo, colors, and typography',
            'budget': 4500.00,
            'deadline': datetime.utcnow() + timedelta(days=35),
            'client_email': 'david@healthtech.com',
            'freelancer_email': 'natalie@graphics.com',
            'status': 'active',
            'project_type': 'Graphic Design',
            'skills': ['Graphic Design', 'Illustration', 'Branding']
        },
        
        # Completed projects (4)
        {
            'title': 'E-commerce Website Design',
            'description': 'Complete e-commerce website design with user-friendly interface',
            'budget': 3000.00,
            'deadline': datetime.utcnow() - timedelta(days=10),
            'client_email': 'sarah@techstartup.com',
            'freelancer_email': 'alex@designer.com',
            'status': 'completed',
            'completed_at': datetime.utcnow() - timedelta(days=5),
            'project_type': 'Web Design',
            'skills': ['UI/UX Design', 'Web Design', 'Figma']
        },
        {
            'title': 'Social Media Campaign',
            'description': 'Comprehensive social media marketing campaign',
            'budget': 4500.00,
            'deadline': datetime.utcnow() - timedelta(days=15),
            'client_email': 'mike@creativeagency.com',
            'freelancer_email': 'priya@developer.com',
            'status': 'completed',
            'completed_at': datetime.utcnow() - timedelta(days=8),
            'project_type': 'Marketing',
            'skills': ['Social Media Marketing', 'Content Writing', 'Analytics']
        },
        {
            'title': 'Corporate Video Production',
            'description': 'Professional corporate video for company branding',
            'budget': 6000.00,
            'deadline': datetime.utcnow() - timedelta(days=20),
            'client_email': 'lisa@edtech.org',
            'freelancer_email': 'ryan@videopro.com',
            'status': 'completed',
            'completed_at': datetime.utcnow() - timedelta(days=12),
            'project_type': 'Video Production',
            'skills': ['Video Editing', 'Premiere Pro', 'Color Grading']
        },
        {
            'title': 'API Backend Development',
            'description': 'RESTful API development for web application',
            'budget': 7500.00,
            'deadline': datetime.utcnow() - timedelta(days=25),
            'client_email': 'james@fintech.io',
            'freelancer_email': 'taylor@fullstack.io',
            'status': 'completed',
            'completed_at': datetime.utcnow() - timedelta(days=18),
            'project_type': 'Web Development',
            'skills': ['Node.js', 'Python', 'PostgreSQL', 'AWS']
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
        
        # Add approval workflow
        project.approved_at = datetime.utcnow() - timedelta(days=random.randint(1, 10))
        project.approved_by = admin_user.id
        
        if 'freelancer_email' in proj_data:
            project.freelancer_id = users[proj_data['freelancer_email']].id
        
        if 'completed_at' in proj_data:
            project.completed_at = proj_data['completed_at']
        
        db.session.add(project)
        db.session.flush()
        
        # Add required skills
        for skill_name in proj_data.get('skills', []):
            if skill_name in skills:
                skill = skills[skill_name]
                project_skill = ProjectSkill(
                    project=project,
                    skill=skill,
                    required_proficiency='intermediate'
                )
                db.session.add(project_skill)
        
        created_projects.append({
            'project': project,
            'client': users[proj_data['client_email']],
            'freelancer': users.get(proj_data.get('freelancer_email'))
        })
        
        print(f"   ✅ {project.status}: {project.title}")
    
    db.session.commit()
    return created_projects

def seed_deliverables(projects_info):
    """Create 3 deliverables matching your count with images"""
    print("\n📦 Creating 3 deliverables...")
    
    sample_images = {
        'UI/UX Design': ['https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800'],
        'Web Design': ['https://images.unsplash.com/photo-1547658719-da2b51169166?w=800'],
        'Video Production': ['https://images.unsplash.com/photo-1536240478700-b869070f9279?w=800'],
        '3D Animation': ['https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800'],
        'Content Writing': ['https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800'],
        'Marketing': ['https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800'],
        'Mobile Development': ['https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800'],
        'Graphic Design': ['https://images.unsplash.com/photo-1559028012-481c04fa702d?w=800']
    }
    
    deliverable_count = 0
    
    for project_info in projects_info[:3]:  # Only create 3 deliverables
        project = project_info['project']
        
        if project.freelancer_id:
            project_type = project.project_type or 'UI/UX Design'
            images = sample_images.get(project_type, sample_images['UI/UX Design'])
            
            deliverable = Deliverable(
                project_id=project.id,
                uploaded_by=project.freelancer_id,
                title=f'Final Deliverable for {project.title}',
                version_number=1,
                file_url=random.choice(images),
                file_type='image',
                thumbnail_url=random.choice(images),
                status='approved',
                description=f'Completed work for {project.title}',
                uploaded_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
            )
            
            deliverable.reviewed_at = deliverable.uploaded_at + timedelta(hours=24)
            deliverable.reviewed_by = project_info['client'].id
            
            db.session.add(deliverable)
            deliverable_count += 1
    
    db.session.commit()
    print(f"   ✅ Created {deliverable_count} deliverables")

def seed_escrows(users, projects_info):
    """Create escrow transactions with all fields"""
    print("\n💰 Creating escrow transactions...")
    
    escrow_count = 0
    
    for project_info in projects_info:
        project = project_info['project']
        
        if project.freelancer_id and project.status in ['active', 'completed']:
            escrow = EscrowTransaction(
                project_id=project.id,
                sender_id=project.client_id,
                receiver_id=project.freelancer_id,
                amount=project.budget,
                currency="USD",
                status='released' if project.status == 'completed' else 'held',
                invoice_number=f"INV-{project.id:04d}-{random.randint(1000, 9999)}",
                invoice_url=f"https://example.com/invoices/INV-{project.id:04d}",
                payment_method="credit_card",
                notes=f"Escrow for project: {project.title}",
                created_at=project.created_at
            )
            
            if project.status == 'completed':
                escrow.released_at = datetime.utcnow() - timedelta(days=5)
            
            db.session.add(escrow)
            escrow_count += 1
    
    db.session.commit()
    print(f"   ✅ Created {escrow_count} escrow transactions")

def seed_feedback():
    """Create 2 feedback items matching your count"""
    print("\n💬 Creating 2 feedback items...")
    
    deliverables = Deliverable.query.all()[:2]  # Only for first 2 deliverables
    
    feedback_messages = [
        "This looks great! Can we make the colors more vibrant?",
        "The design is clean but needs better spacing."
    ]
    
    for i, deliverable in enumerate(deliverables):
        feedback = Feedback(
            deliverable_id=deliverable.id,
            user_id=deliverable.project.client_id,
            feedback_type='revision',
            content=feedback_messages[i],
            priority='medium',
            is_resolved=False,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(feedback)
    
    db.session.commit()
    print("   ✅ Created 2 feedback items")

def seed_reviews(projects_info):
    """Create reviews for completed projects"""
    print("\n⭐ Creating reviews...")
    
    review_comments = [
        "Excellent work! Very professional and delivered on time.",
        "Great communication and quality work. Highly recommended!"
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
                review_text=review_comments[review_count % len(review_comments)],
                created_at=project.completed_at + timedelta(days=1)
            )
            db.session.add(review)
            review_count += 1
    
    db.session.commit()
    print(f"   ✅ Created {review_count} reviews")

def seed_invoices(projects_info):
    """Create invoices"""
    print("\n🧾 Creating invoices...")
    
    invoice_statuses = ['unpaid', 'paid', 'overdue']
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
    print(f"   ✅ Created {invoice_count} invoices")

def seed_activity_logs(users, projects_info):
    """Create activity logs"""
    print("\n📊 Creating activity logs...")
    
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

def seed_wallets(users):
    """Create wallets for users"""
    print("\n💳 Creating wallets...")
    
    for user in users.values():
        wallet = Wallet(
            user_id=user.id,
            balance=Decimal('1000.00') if user.role == 'client' else Decimal('500.00'),
            currency="USD"
        )
        db.session.add(wallet)
    
    db.session.commit()
    print("   ✅ Created wallets for all users")

def print_success_message():
    """Print success message"""
    print("\n" + "="*70)
    print("🎉 COMPREHENSIVE DATABASE SEEDING COMPLETE!")
    print("="*70)
    
    print(f"\n📊 FINAL COUNTS (MATCHING YOUR EXISTING):")
    print(f"   👥 Users: {User.query.count()} (6 clients, 12 freelancers, 1 admin)")
    print(f"   📁 Projects: {Project.query.count()}")
    print(f"   📦 Deliverables: {Deliverable.query.count()}")
    print(f"   💬 Feedback: {Feedback.query.count()}")
    print(f"   ⭐ Reviews: {Review.query.count()}")
    print(f"   📊 Activities: {ActivityLog.query.count()}")
    
    print(f"\n🚀 READY FOR ALL 110 ENDPOINTS:")
    print(f"   Auth: /api/auth/register, /api/auth/login, /api/auth/refresh")
    print(f"   Projects: /api/projects, /api/projects/<id>")
    print(f"   Deliverables: /api/deliverable/projects/<id>")
    print(f"   Freelancers: /api/freelancers/, /api/freelancers/pending")
    print(f"   Escrow: /api/escrow/, /api/escrow/create")
    print(f"   Dashboard: /api/dashboard/stats, /api/dashboard/activity")
    
    print(f"\n🔑 TEST CREDENTIALS:")
    print(f"   Admin:      admin@reelbrief.com / admin123")
    print(f"   Client:     sarah@techstartup.com / client123") 
    print(f"   Freelancer: alex@designer.com / freelancer123")
    
    print("="*70)

def seed_database():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print("🌱 COMPREHENSIVE DATABASE SEEDING STARTING")
        print("📊 Matching 110 backend endpoints + frontend API flow")
        print("="*70)
        
        try:
            clear_existing_data()
            skills = seed_skills()
            users = seed_users()
            projects_info = seed_projects(users)
            seed_escrows(users, projects_info)
            seed_deliverables(projects_info)
            seed_feedback()
            seed_reviews(projects_info)
            seed_invoices(projects_info)
            seed_activity_logs(users, projects_info)
            seed_wallets(users)
            
            print_success_message()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    seed_database()