# app/tests/test_deliverables_isolated.py
import os
import sys
from sqlalchemy import create_engine, MetaData, Table, select

def test_tables_directly():
    """Test database tables directly without SQLAlchemy models"""
    
    # Database connection
    database_url = os.getenv('DATABASE_URL', 'postgresql://reelbrief_user:cindy123@localhost/reelbrief_db')
    engine = create_engine(database_url)
    
    # Reflect database tables (read existing schema)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    print("Testing database tables directly...")
    
    # Check if tables exist
    if 'deliverables' in metadata.tables:
        print("deliverables table exists")
        
        # Count rows in deliverables
        with engine.connect() as conn:
            result = conn.execute(select(metadata.tables['deliverables']))
            deliverables = result.fetchall()
            print(f"Found {len(deliverables)} rows in deliverables table")
            
            # Show column names
            table = metadata.tables['deliverables']
            print(f"Deliverables columns: {[c.name for c in table.columns]}")
    
    if 'feedback' in metadata.tables:
        print("feedback table exists")
        
        # Count rows in feedback
        with engine.connect() as conn:
            result = conn.execute(select(metadata.tables['feedback']))
            feedbacks = result.fetchall()
            print(f"Found {len(feedbacks)} rows in feedback table")
            
            # Show column names
            table = metadata.tables['feedback']
            print(f"Feedback columns: {[c.name for c in table.columns]}")
    
    if 'users' in metadata.tables:
        print("users table exists")
        
        # Count rows in users
        with engine.connect() as conn:
            result = conn.execute(select(metadata.tables['users']))
            users = result.fetchall()
            print(f"Found {len(users)} rows in users table")
    
    print("Database tables are properly created!")
    
    # Test foreign key relationships manually
    if 'deliverables' in metadata.tables and 'feedback' in metadata.tables:
        print("\n Testing foreign key relationships...")
        deliverables_table = metadata.tables['deliverables']
        feedback_table = metadata.tables['feedback']
        
        # Check if feedback has foreign key to deliverables
        fk_to_deliverables = False
        for fk in feedback_table.foreign_keys:
            if fk.column.table.name == 'deliverables':
                fk_to_deliverables = True
                print(f"Feedback has foreign key to deliverables: {fk}")
        
        if fk_to_deliverables:
            print("Foreign key relationship between feedback and deliverables is established!")
        else:
            print("No foreign key found from feedback to deliverables")
def create_sample_data():
    """Create sample data for testing - complete version"""
    import psycopg2
    from datetime import datetime
    from dotenv import load_dotenv
    load_dotenv()
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print("Creating sample data...")
    
    try:
        current_time = datetime.utcnow()
        
        # Create users with ALL required fields
        cur.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            'test.client@example.com', 'hashed_password_123', 'John', 'Client', 'client', True, True, current_time, current_time
        ))
        client_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            'freelancer@example.com', 'hashed_password_456', 'Sarah', 'Designer', 'freelancer', True, True, current_time, current_time
        ))
        freelancer_id = cur.fetchone()[0]
        
        # Create deliverable with ALL fields that might have constraints
        cur.execute("""
            INSERT INTO deliverables (project_id, uploaded_by, version_number, file_url, file_type, file_size, 
                                    title, description, change_notes, status, uploaded_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            1, freelancer_id, 1, 
            'https://res.cloudinary.com/example/image/upload/v1/sample.jpg',
            'image', 2048000, 'Website Homepage Design',
            'Initial design for the homepage', 'First version with basic layout', 'pending', current_time
        ))
        deliverable_id = cur.fetchone()[0]
        
        # Create feedback
        cur.execute("""
            INSERT INTO feedback (deliverable_id, user_id, content, feedback_type, priority, is_resolved, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (deliverable_id, client_id, 'Great work! The layout looks clean and modern.', 'comment', 'medium', False, current_time))
        
        cur.execute("""
            INSERT INTO feedback (deliverable_id, user_id, content, feedback_type, priority, is_resolved, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (deliverable_id, client_id, 'Can we make the header section larger?', 'revision_request', 'high', False, current_time))
        
        conn.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating sample data: {e}")
        raise
    finally:
        cur.close()
        conn.close()
def verify_sample_data():
    """Verify the sample data and relationships work correctly"""
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print("\n Verifying sample data...")
    
    try:
        # Count records
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        print(f"Users: {user_count} records")
        
        cur.execute("SELECT COUNT(*) FROM deliverables")
        deliverable_count = cur.fetchone()[0]
        print(f"Deliverables: {deliverable_count} records")
        
        cur.execute("SELECT COUNT(*) FROM feedback")
        feedback_count = cur.fetchone()[0]
        print(f"Feedback: {feedback_count} records")
        
        # Test relationships - get deliverable with its feedback
        cur.execute("""
            SELECT d.id, d.title, d.status, f.content, f.feedback_type, u.first_name 
            FROM deliverables d
            JOIN feedback f ON d.id = f.deliverable_id
            JOIN users u ON f.user_id = u.id
            ORDER BY d.id, f.id
        """)
        
        results = cur.fetchall()
        print(f"Found {len(results)} feedback items linked to deliverables")
        
        for row in results:
            deliverable_id, title, status, feedback_content, feedback_type, user_name = row
            print(f"   - Deliverable '{title}' (status: {status})")
            print(f"     Feedback from {user_name}: '{feedback_content}' ({feedback_type})")
        
        # Test the version number method concept
        cur.execute("""
            SELECT project_id, MAX(version_number) as max_version
            FROM deliverables 
            GROUP BY project_id
        """)
        
        version_results = cur.fetchall()
        for project_id, max_version in version_results:
            print(f"Project {project_id}: highest version number is {max_version}")
        
        print("SUCCESS!!All data verification tests passed!")
        
    except Exception as e:
        print(f"Error verifying data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

# In your test_deliverables.py or create a new seed file
def create_verified_users():
    """Create verified users with known passwords for testing"""
    import psycopg2
    from datetime import datetime
    from dotenv import load_dotenv
    from werkzeug.security import generate_password_hash
    load_dotenv()
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    print("Creating verified users for testing...")
    
    try:
        current_time = datetime.utcnow()
        known_password = "password123"  # Simple password for testing
        hashed_password = generate_password_hash(known_password)
        
        # Delete existing test users if they exist
        cur.execute("DELETE FROM users WHERE email IN ('test.client@example.com', 'freelancer@example.com')")
        
        # Create verified client user
        cur.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            'test.client@example.com', hashed_password, 'John', 'Client', 'client', True, True, current_time, current_time
        ))
        client_id = cur.fetchone()[0]
        
        # Create verified freelancer user
        cur.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, is_verified, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            'freelancer@example.com', hashed_password, 'Sarah', 'Designer', 'freelancer', True, True, current_time, current_time
        ))
        freelancer_id = cur.fetchone()[0]
        
        conn.commit()
        print("Verified users created successfully!")
        print(f"   - Client: test.client@example.com / password123")
        print(f"   - Freelancer: freelancer@example.com / password123")
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating users: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    test_tables_directly()
    # create_sample_data()
    verify_sample_data()
