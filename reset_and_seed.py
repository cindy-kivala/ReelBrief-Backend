#!/usr/bin/env python3
from app import create_app
from app.extensions import db

def reset_database():
    """Safely reset the database considering foreign key constraints"""
    app = create_app()
    with app.app_context():
        print("🔄 Resetting database...")
        
        # Drop all tables and recreate them
        db.drop_all()
        print("✅ Tables dropped")
        
        db.create_all()
        print("✅ Tables recreated")
        
        db.session.commit()
        print("✅ Database reset complete")

if __name__ == "__main__":
    reset_database()
