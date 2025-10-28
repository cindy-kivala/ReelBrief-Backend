# init_db.py
"""
Complete database initialization script
Creates all tables and seeds test data
"""

from app import create_app, db
from sqlalchemy import inspect, text

def init_database():
    app = create_app()
    
    with app.app_context():
        print("🚀 Initializing PostgreSQL Database")
        print("=" * 60)
        
        try:
            # Import all models
            from app.models import User, Project, Deliverable, Feedback
            
            print("📋 Models imported successfully")
            
            # Create all tables
            print("\n1️⃣ Creating tables...")
            db.create_all()
            print("   ✅ All tables created!")
            
            # Verify tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n📊 Database has {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   - {table}")
            
            # Seed test users
            print("\n2️⃣ Seeding test users...")
            users_data = [
                {
                    'email': 'cindy_freelancer@example.com',
                    'password': 'freelancer123',
                    'first_name': 'Cindy',
                    'last_name': 'Freelancer',
                    'role': 'freelancer'
                },
                {
                    'email': 'cindy_client@example.com',
                    'password': 'client123',
                    'first_name': 'Test',
                    'last_name': 'Client',
                    'role': 'client'
                }
            ]
            
            for user_data in users_data:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                
                if existing_user:
                    print(f"   ⏭️  {user_data['email']} exists")
                else:
                    user = User(
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role=user_data['role']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    print(f"   ✅ Created {user_data['email']}")
            
            db.session.commit()
            
            # Create test project
            print("\n3️⃣ Creating test project...")
            test_project = Project.query.filter_by(title='Cindy Test Project').first()
            
            if not test_project:
                test_project = Project(title='Cindy Test Project')
                db.session.add(test_project)
                db.session.commit()
                print(f"   ✅ Created project (ID: {test_project.id})")
            else:
                print(f"   ⏭️  Test project exists (ID: {test_project.id})")
            
            print("\n" + "=" * 60)
            print("🎉 DATABASE INITIALIZATION COMPLETE!")
            print("=" * 60)
            
            # Display summary
            print("\n📊 Summary:")
            print(f"   Users: {User.query.count()}")
            print(f"   Projects: {Project.query.count()}")
            print(f"   Deliverables: {Deliverable.query.count()}")
            print(f"   Feedback: {Feedback.query.count()}")
            
            print("\n🔑 Test Credentials:")
            print("   Freelancer: cindy_freelancer@example.com / freelancer123")
            print("   Client: cindy_client@example.com / client123")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)