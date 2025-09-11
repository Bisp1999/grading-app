#!/usr/bin/env python3
"""
Database migration script to add ClassroomLayout table
Run this script to add the new table for persistent classroom layouts
"""

import sqlite3
import os

def add_classroom_layout_table():
    """Add the ClassroomLayout table to the database"""
    db_path = os.path.join('instance', 'grading_app.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classroom_layout';")
        if cursor.fetchone():
            print("✅ ClassroomLayout table already exists")
            conn.close()
            return
        
        # Create the ClassroomLayout table
        create_table_sql = """
        CREATE TABLE classroom_layout (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            classroom_id INTEGER NOT NULL,
            layout_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teacher (id),
            FOREIGN KEY (classroom_id) REFERENCES classroom (id),
            UNIQUE (teacher_id, classroom_id)
        );
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        
        print("✅ ClassroomLayout table created successfully!")
        
        # Verify the table was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='classroom_layout';")
        if cursor.fetchone():
            print("✅ ClassroomLayout table verified in database")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(classroom_layout);")
            columns = cursor.fetchall()
            print("\nTable structure:")
            for column in columns:
                print(f"  - {column[1]}: {column[2]}")
        else:
            print("❌ ClassroomLayout table not found after creation")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating ClassroomLayout table: {e}")

if __name__ == '__main__':
    add_classroom_layout_table()
