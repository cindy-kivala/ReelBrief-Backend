#!/usr/bin/env python3
from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

def simple_seed():
    """Simple seed with just users to test basic functionality"""
    app = create_app()
    with app.app_context():
        print("🚀 Simple database seeding...")
        
        # Clear existing users safely
        try:
            # Delete users in the right order to avoid foreign key constraints
            db.session.query(User).delete()
            db.session.commit()
            print("✅ Cleared existing users")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️  Could not clear users: {e}")
        
        # Create basic test users
        users = [
            User(
                first_name="Admin",
                last_name="User", 
                email="admin@reelbrief.com",
                password_hash=generate_password_hash("admin123"),
                role="admin"
            ),
            User(
                first_name="Freelancer",
                last_name="One",
                email="freelancer@reelbrief.com", 
                password_hash=generate_password_hash("freelancer123"),
                role="freelancer"
            ),
            User(
                first_name="Client",
                last_name="One",
                email="client@reelbrief.com",
                password_hash=generate_password_hash("client123"), 
                role="client"
            ),
        ]
        
        for user in users:
            db.session.add(user)
            print(f"✅ Added user: {user.email} ({user.role})")
        
        db.session.commit()
        print("🎉 Simple seeding complete!")
        
        # Show what was created
        user_count = User.query.count()
        print(f"📊 Total users in database: {user_count}")

if __name__ == "__main__":
    simple_seed()
