# fix_escrow_constraints.py
import os
os.environ['DATABASE_URL'] = "postgresql://reelbrief_user:ogql1kUnTziHY3TYQSa8PYmcN7LZoJxA@dpg-d3qi0pili9vc73ccpf30-a.oregon-postgres.render.com/reelbrief_db"

from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Making old escrow columns nullable...")
    
    try:
        with db.engine.connect() as conn:
            # Make old columns nullable
            conn.execute(text('ALTER TABLE escrow_transactions ALTER COLUMN client_id DROP NOT NULL'))
            conn.execute(text('ALTER TABLE escrow_transactions ALTER COLUMN freelancer_id DROP NOT NULL'))
            conn.execute(text('ALTER TABLE escrow_transactions ALTER COLUMN admin_id DROP NOT NULL'))
            
            conn.commit()
        
        print("Made old columns nullable!")
        
    except Exception as e:
        print(f"Error: {e}")