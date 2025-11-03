from app import create_app
from app.extensions import db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    
    print("=" * 60)
    print("DATABASE SCHEMA ANALYSIS")
    print("=" * 60)
    
    tables = inspector.get_table_names()
    print(f"\n📊 TOTAL TABLES: {len(tables)}")
    
    for table in sorted(tables):
        print(f"\n🏷️  TABLE: {table}")
        print("-" * 40)
        
        columns = inspector.get_columns(table)
        print("  Columns:")
        for col in columns:
            pk = " (PK)" if col.get('primary_key', False) else ""
            fk = " (FK)" if col.get('foreign_keys') else ""
            nullable = " (NULL)" if col['nullable'] else " (NOT NULL)"
            default = f" [default: {col['default']}]" if col['default'] else ""
            print(f"    - {col['name']}: {col['type']}{pk}{fk}{nullable}{default}")
        
        fks = inspector.get_foreign_keys(table)
        if fks:
            print("  Foreign Keys:")
            for fk in fks:
                print(f"    - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
