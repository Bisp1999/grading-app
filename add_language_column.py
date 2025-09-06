#!/usr/bin/env python3
"""
Database migration script to add preferred_language column to Teacher table
"""

import sqlite3
import os

def add_language_column():
    # Get the database path
    db_path = os.path.join('instance', 'grading_app.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(teacher)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'preferred_language' in columns:
            print("preferred_language column already exists")
            return True
        
        # Add the preferred_language column
        cursor.execute("""
            ALTER TABLE teacher 
            ADD COLUMN preferred_language VARCHAR(5) DEFAULT 'en' NOT NULL
        """)
        
        conn.commit()
        print("Successfully added preferred_language column to teacher table")
        return True
        
    except Exception as e:
        print(f"Error adding preferred_language column: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    add_language_column()
