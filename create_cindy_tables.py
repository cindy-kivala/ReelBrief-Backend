# create_all_tables.py
from app import create_app, db
from sqlalchemy import inspect

def create_cindy_tables():
    app = create_app()
    
    with app.app_context():
        print("🚀 Creating all PostgreSQL tables...")
        
        try:
            # Import all models to ensure they're registered with SQLAlchemy
            from app.models.user import User
            from app.models.deliverable import Deliverable
            from app.models.feedback import Feedback
            
            # Create a minimal Project model since it's referenced by Deliverable
            class Project(db.Model):
                __tablename__ = 'projects'
                id = db.Column(db.Integer, primary_key=True)
                title = db.Column(db.String(255), default='Test Project')
            
            print("📋 Models imported successfully")
            
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Verify
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print("📊 Tables in your PostgreSQL database:")
            for table in sorted(tables):
                print(f"   - {table}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_cindy_tables()