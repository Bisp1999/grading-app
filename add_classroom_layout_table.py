#!/usr/bin/env python3
"""
Database migration script to add ClassroomLayout table
Run this script to add the new table for persistent classroom layouts
"""

from app import create_app, db
from app.models import ClassroomLayout

def add_classroom_layout_table():
    """Add the ClassroomLayout table to the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the ClassroomLayout table
            db.create_all()
            print("✅ ClassroomLayout table created successfully!")
            
            # Verify the table was created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'classroom_layout' in tables:
                print("✅ ClassroomLayout table verified in database")
                
                # Show table structure
                columns = inspector.get_columns('classroom_layout')
                print("\nTable structure:")
                for column in columns:
                    print(f"  - {column['name']}: {column['type']}")
            else:
                print("❌ ClassroomLayout table not found")
                
        except Exception as e:
            print(f"❌ Error creating ClassroomLayout table: {e}")

if __name__ == '__main__':
    add_classroom_layout_table()
