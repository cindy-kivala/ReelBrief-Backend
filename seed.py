# seed.py
"""
Complete database seeding script for ReelBrief project presentation
Creates realistic demo data for all features
"""

from app import create_app, db
from app.models import User, Project, Deliverable, Feedback, FreelancerProfile
from datetime import datetime, timedelta
from sqlalchemy import text
import random

def clear_database():
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    try:
        # Delete in correct order to respect foreign keys
        db.session.execute(text("DELETE FROM feedback"))
        db.session.execute(text("DELETE FROM deliverables"))
        db.session.execute(text("DELETE FROM freelancer_profiles"))
        db.session.execute(text("DELETE FROM projects"))
        db.session.execute(text("DELETE FROM users WHERE email LIKE '%@demo.com' OR email LIKE '%@example.com'"))
        db.session.commit()
        print("   ✅ Database cleared")
    except Exception as e:
        db.session.rollback()
        print(f"   ⚠️  Error clearing database: {e}")

def seed_users():
    """Create demo users"""
    print("\n👥 Creating demo users...")
    
    users_data = [
        # Clients
        {
            'email': 'sarah.johnson@techstartup.com',
            'password': 'demo123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'client',
            'description': 'CEO of TechStartup Inc.'
        },
        {
            'email': 'mike.chen@creativeagency.com',
            'password': 'demo123',
            'first_name': 'Mike',
            'last_name': 'Chen',
            'role': 'client',
            'description': 'Creative Director'
        },
        {
            'email': 'emily.rodriguez@brandco.com',
            'password': 'demo123',
            'first_name': 'Emily',
            'last_name': 'Rodriguez',
            'role': 'client',
            'description': 'Marketing Manager'
        },
        
        # Freelancers
        {
            'email': 'alex.designer@demo.com',
            'password': 'demo123',
            'first_name': 'Alex',
            'last_name': 'Thompson',
            'role': 'freelancer',
            'description': 'UI/UX Designer specializing in mobile apps',
            'profile': {
                'bio': '5+ years of experience in UI/UX design. Passionate about creating intuitive user experiences.',
                'skills': 'Figma, Adobe XD, Sketch, Prototyping, User Research',
                'hourly_rate': 85.00,
                'portfolio_url': 'https://alexthompson.design'
            }
        },
        {
            'email': 'priya.developer@demo.com',
            'password': 'demo123',
            'first_name': 'Priya',
            'last_name': 'Patel',
            'role': 'freelancer',
            'description': 'Full-stack developer and video editor',
            'profile': {
                'bio': 'Full-stack developer with expertise in React, Node.js, and video production.',
                'skills': 'React, Node.js, Python, Video Editing, Motion Graphics',
                'hourly_rate': 95.00,
                'portfolio_url': 'https://priyapatel.dev'
            }
        },
        {
            'email': 'carlos.animator@demo.com',
            'password': 'demo123',
            'first_name': 'Carlos',
            'last_name': 'Martinez',
            'role': 'freelancer',
            'description': '3D animator and motion graphics artist',
            'profile': {
                'bio': 'Award-winning 3D animator specializing in product visualization and motion graphics.',
                'skills': 'Blender, Cinema 4D, After Effects, Motion Graphics',
                'hourly_rate': 110.00,
                'portfolio_url': 'https://carlosanimation.com'
            }
        },
        
        # Admin
        {
            'email': 'admin@reelbrief.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin',
            'description': 'Platform Administrator'
        }
    ]
    
    created_users = {}
    
    for user_data in users_data:
        user = User(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create freelancer profile if applicable
        if 'profile' in user_data:
            profile = FreelancerProfile(
                user_id=user.id,
                bio=user_data['profile']['bio'],
                skills=user_data['profile']['skills'],
                hourly_rate=user_data['profile']['hourly_rate'],
                portfolio_url=user_data['profile']['portfolio_url']
            )
            db.session.add(profile)
        
        created_users[user_data['email']] = user
        print(f"   ✅ Created {user.role}: {user.email}")
    
    db.session.commit()
    return created_users

def seed_projects(users):
    """Create demo projects"""
    print("\n📁 Creating demo projects...")
    
    projects_data = [
        {
            'title': 'Mobile App Redesign - TechStartup',
            'description': 'Complete UI/UX redesign for our flagship mobile application',
            'client_email': 'sarah.johnson@techstartup.com',
            'freelancer_email': 'alex.designer@demo.com',
            'status': 'active'
        },
        {
            'title': 'Product Launch Video - CreativeAgency',
            'description': 'Create a 60-second promotional video for new product launch',
            'client_email': 'mike.chen@creativeagency.com',
            'freelancer_email': 'priya.developer@demo.com',
            'status': 'active'
        },
        {
            'title': 'Brand Animation Package - BrandCo',
            'description': '3D logo animation and brand identity motion graphics',
            'client_email': 'emily.rodriguez@brandco.com',
            'freelancer_email': 'carlos.animator@demo.com',
            'status': 'active'
        },
        {
            'title': 'Website Wireframes - TechStartup',
            'description': 'Wireframes and prototypes for company website redesign',
            'client_email': 'sarah.johnson@techstartup.com',
            'freelancer_email': 'alex.designer@demo.com',
            'status': 'completed'
        }
    ]
    
    created_projects = []
    
    for proj_data in projects_data:
        project = Project(
            title=proj_data['title'],
            created_at=datetime.utcnow() - timedelta(days=random.randint(5, 30))
        )
        db.session.add(project)
        db.session.flush()
        
        created_projects.append({
            'project': project,
            'client': users[proj_data['client_email']],
            'freelancer': users[proj_data['freelancer_email']]
        })
        
        print(f"   ✅ Created project: {project.title}")
    
    db.session.commit()
    return created_projects

def seed_deliverables(projects_info):
    """Create demo deliverables with realistic progression"""
    print("\n📦 Creating deliverables...")
    
    deliverables_data = [
        # Project 1: Mobile App Redesign (Multiple versions showing iteration)
        {
            'project_idx': 0,
            'items': [
                {
                    'title': 'Initial Wireframes',
                    'version': 1,
                    'status': 'approved',
                    'file_url': 'https://res.cloudinary.com/demo/wireframes-v1.pdf',
                    'description': 'Initial low-fidelity wireframes for all main screens',
                    'days_ago': 20,
                    'file_type': 'document'
                },
                {
                    'title': 'Revised Wireframes',
                    'version': 2,
                    'status': 'approved',
                    'file_url': 'https://res.cloudinary.com/demo/wireframes-v2.pdf',
                    'description': 'Updated wireframes based on client feedback',
                    'change_notes': 'Added onboarding flow, simplified navigation',
                    'days_ago': 15,
                    'file_type': 'document'
                },
                {
                    'title': 'High-Fidelity Mockups',
                    'version': 3,
                    'status': 'revision_requested',
                    'file_url': 'https://res.cloudinary.com/demo/mockups-v1.fig',
                    'description': 'Full color mockups with final design system',
                    'change_notes': 'Applied brand colors, typography, and icons',
                    'days_ago': 8,
                    'file_type': 'image'
                },
                {
                    'title': 'Final Mockups - Revised',
                    'version': 4,
                    'status': 'pending',
                    'file_url': 'https://res.cloudinary.com/demo/mockups-v2.fig',
                    'description': 'Updated mockups addressing revision requests',
                    'change_notes': 'Improved color contrast, updated button styles',
                    'days_ago': 2,
                    'file_type': 'image'
                }
            ]
        },
        
        # Project 2: Product Launch Video (Video production workflow)
        {
            'project_idx': 1,
            'items': [
                {
                    'title': 'Storyboard Draft',
                    'version': 1,
                    'status': 'approved',
                    'file_url': 'https://res.cloudinary.com/demo/storyboard-v1.pdf',
                    'description': 'Visual storyboard for 60-second product video',
                    'days_ago': 12,
                    'file_type': 'document'
                },
                {
                    'title': 'Rough Cut',
                    'version': 2,
                    'status': 'approved',
                    'file_url': 'https://res.cloudinary.com/demo/rough-cut.mp4',
                    'description': 'Initial video edit without color grading',
                    'change_notes': 'Assembled footage per storyboard',
                    'days_ago': 7,
                    'file_type': 'video'
                },
                {
                    'title': 'Final Cut with Graphics',
                    'version': 3,
                    'status': 'pending',
                    'file_url': 'https://res.cloudinary.com/demo/final-cut.mp4',
                    'description': 'Color graded video with motion graphics',
                    'change_notes': 'Added transitions, color grading, and text animations',
                    'days_ago': 1,
                    'file_type': 'video'
                }
            ]
        },
        
        # Project 3: Brand Animation Package
        {
            'project_idx': 2,
            'items': [
                {
                    'title': 'Logo Animation Concept',
                    'version': 1,
                    'status': 'approved',
                    'file_url': 'https://res.cloudinary.com/demo/logo-concept.mp4',
                    'description': '3 different logo animation concepts',
                    'days_ago': 10,
                    'file_type': 'video'
                },
                {
                    'title': 'Final Logo Animation',
                    'version': 2,
                    'status': 'approved',
                    'file_url': 'https://res.cloudinary.com/demo/logo-final.mp4',
                    'description': 'Refined logo animation (5 seconds)',
                    'change_notes': 'Selected concept #2, added sound design',
                    'days_ago': 5,
                    'file_type': 'video'
                },
                {
                    'title': 'Brand Elements Package',
                    'version': 3,
                    'status': 'pending',
                    'file_url': 'https://res.cloudinary.com/demo/brand-package.zip',
                    'description': 'Complete package: logo animation + lower thirds + transitions',
                    'change_notes': 'Added 5 lower third templates and 3 transition effects',
                    'days_ago': 1,
                    'file_type': 'document'
                }
            ]
        },
        
        # Project 4: Website Wireframes (Completed project)
        {
            'project_idx': 3,
            'items': [
                {
                    'title': 'Homepage Wireframes',
                    'version': 1,
                    'status': 'approved',
                    'file_url': 'https://res.cloudinary.com/demo/homepage-wireframe.pdf',
                    'description': 'Homepage layout and structure',
                    'days_ago': 25,
                    'file_type': 'document'
                },
                {
                    'title': 'Complete Sitemap',
                    'version': 2,
                    'status': 'approved',
                    'file_url': 'https://res.cloudinary.com/demo/sitemap.pdf',
                    'description': 'All pages wireframed with navigation flow',
                    'change_notes': 'Added 15 page layouts, user flow diagrams',
                    'days_ago': 18,
                    'file_type': 'document'
                }
            ]
        }
    ]
    
    created_deliverables = []
    
    for proj_data in deliverables_data:
        project_info = projects_info[proj_data['project_idx']]
        project = project_info['project']
        freelancer = project_info['freelancer']
        
        for item in proj_data['items']:
            upload_date = datetime.utcnow() - timedelta(days=item['days_ago'])
            
            deliverable = Deliverable(
                project_id=project.id,
                uploaded_by=freelancer.id,
                title=item['title'],
                version_number=item['version'],
                file_url=item['file_url'],
                file_type=item.get('file_type', 'document'),
                status=item['status'],
                description=item['description'],
                change_notes=item.get('change_notes'),
                uploaded_at=upload_date
            )
            
            # Set reviewed_at for approved items
            if item['status'] in ['approved', 'revision_requested']:
                deliverable.reviewed_at = upload_date + timedelta(hours=random.randint(2, 48))
                deliverable.reviewed_by = project_info['client'].id
            
            db.session.add(deliverable)
            db.session.flush()
            
            created_deliverables.append({
                'deliverable': deliverable,
                'project_info': project_info
            })
    
    db.session.commit()
    print(f"   ✅ Created {len(created_deliverables)} deliverables")
    return created_deliverables

def seed_feedback(deliverables_info):
    """Create realistic feedback on deliverables"""
    print("\n💬 Creating feedback...")
    
    feedback_scenarios = [
        # Feedback on Mobile App Redesign v3 (revision requested)
        {
            'deliverable_title': 'High-Fidelity Mockups',
            'items': [
                {
                    'content': 'Overall design looks great! However, I have a few concerns about the color contrast on the main CTA buttons. Can we make them more prominent?',
                    'feedback_type': 'revision',
                    'priority': 'high',
                    'is_resolved': False,
                    'days_ago': 7
                },
                {
                    'content': 'The navigation feels a bit cluttered on smaller screens. Could we simplify it for mobile?',
                    'feedback_type': 'revision',
                    'priority': 'medium',
                    'is_resolved': False,
                    'days_ago': 7
                },
                {
                    'content': 'Love the icon set you chose! Really modern and clean.',
                    'feedback_type': 'comment',
                    'priority': 'low',
                    'is_resolved': True,
                    'days_ago': 7,
                    'reply': {
                        'content': 'Thank you! I designed them specifically to match your brand style.',
                        'days_ago': 6
                    }
                }
            ]
        },
        
        # Feedback on Product Launch Video v2 (approved)
        {
            'deliverable_title': 'Rough Cut',
            'items': [
                {
                    'content': 'The pacing is perfect! Really captures the energy we wanted.',
                    'feedback_type': 'approval',
                    'priority': 'medium',
                    'is_resolved': True,
                    'days_ago': 6
                },
                {
                    'content': 'Can we add some motion graphics to highlight the key features around the 30-second mark?',
                    'feedback_type': 'revision',
                    'priority': 'medium',
                    'is_resolved': True,
                    'days_ago': 6,
                    'reply': {
                        'content': 'Absolutely! I\'ll add animated callouts and text overlays in the final cut.',
                        'days_ago': 6
                    }
                }
            ]
        },
        
        # Feedback on Brand Animation v1 (approved)
        {
            'deliverable_title': 'Logo Animation Concept',
            'items': [
                {
                    'content': 'We love concept #2! The smooth rotation really makes the logo pop. Let\'s go with that one.',
                    'feedback_type': 'approval',
                    'priority': 'high',
                    'is_resolved': True,
                    'days_ago': 9
                }
            ]
        },
        
        # Feedback on Mobile App Redesign v2 (approved)
        {
            'deliverable_title': 'Revised Wireframes',
            'items': [
                {
                    'content': 'The onboarding flow is much clearer now. Approved to move to high-fidelity mockups!',
                    'feedback_type': 'approval',
                    'priority': 'high',
                    'is_resolved': True,
                    'days_ago': 14
                }
            ]
        }
    ]
    
    feedback_count = 0
    
    for scenario in feedback_scenarios:
        # Find the deliverable
        deliverable_info = next(
            (d for d in deliverables_info if d['deliverable'].title == scenario['deliverable_title']),
            None
        )
        
        if not deliverable_info:
            continue
        
        deliverable = deliverable_info['deliverable']
        client = deliverable_info['project_info']['client']
        freelancer = deliverable_info['project_info']['freelancer']
        
        for item in scenario['items']:
            created_at = datetime.utcnow() - timedelta(days=item['days_ago'])
            
            feedback = Feedback(
                deliverable_id=deliverable.id,
                user_id=client.id,
                feedback_type=item['feedback_type'],
                content=item['content'],
                priority=item['priority'],
                is_resolved=item['is_resolved'],
                created_at=created_at
            )
            
            if item['is_resolved']:
                feedback.resolved_at = created_at + timedelta(hours=random.randint(1, 24))
            
            db.session.add(feedback)
            db.session.flush()
            feedback_count += 1
            
            # Add reply if specified
            if 'reply' in item:
                reply = Feedback(
                    deliverable_id=deliverable.id,
                    user_id=freelancer.id,
                    parent_feedback_id=feedback.id,
                    feedback_type='comment',
                    content=item['reply']['content'],
                    priority='low',
                    is_resolved=True,
                    created_at=datetime.utcnow() - timedelta(days=item['reply']['days_ago'])
                )
                db.session.add(reply)
                feedback_count += 1
    
    db.session.commit()
    print(f"   ✅ Created {feedback_count} feedback items")

def print_summary(users):
    """Print summary of seeded data"""
    print("\n" + "=" * 70)
    print("🎉 DATABASE SEEDING COMPLETE!")
    print("=" * 70)
    
    print("\n📊 Summary:")
    print(f"   Users: {User.query.count()}")
    print(f"   Projects: {Project.query.count()}")
    print(f"   Deliverables: {Deliverable.query.count()}")
    print(f"   Feedback Items: {Feedback.query.count()}")
    
    print("\n🔑 Demo Credentials:")
    print("\n   CLIENTS:")
    print("   • sarah.johnson@techstartup.com / demo123")
    print("   • mike.chen@creativeagency.com / demo123")
    print("   • emily.rodriguez@brandco.com / demo123")
    
    print("\n   FREELANCERS:")
    print("   • alex.designer@demo.com / demo123 (UI/UX Designer)")
    print("   • priya.developer@demo.com / demo123 (Full-stack Dev)")
    print("   • carlos.animator@demo.com / demo123 (3D Animator)")
    
    print("\n   ADMIN:")
    print("   • admin@reelbrief.com / admin123")
    
    print("\n💡 Demo Scenarios Ready:")
    print("   ✅ Active projects with multiple deliverable versions")
    print("   ✅ Realistic feedback and revision workflows")
    print("   ✅ Approved, pending, and revision-requested deliverables")
    print("   ✅ Threaded feedback conversations")
    print("   ✅ Freelancer profiles with portfolios")
    
    print("\n" + "=" * 70)

def seed_database():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Seeding ReelBrief Database for Presentation")
        print("=" * 70)
        
        try:
            # Optionally clear existing demo data
            clear = input("\n⚠️  Clear existing data? (y/N): ").lower()
            if clear == 'y':
                clear_database()
            
            # Seed data in order
            users = seed_users()
            projects_info = seed_projects(users)
            deliverables_info = seed_deliverables(projects_info)
            seed_feedback(deliverables_info)
            
            # Print summary
            print_summary(users)
            
            print("\n✨ Your database is ready for the presentation!")
            print("🚀 Start your Flask server and login with any demo account\n")
            
        except Exception as e:
            print(f"\n❌ Error seeding database: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    seed_database()