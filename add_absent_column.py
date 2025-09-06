#!/usr/bin/env python3
"""
Database migration script to add 'absent' column to Grade table
"""
import sqlite3
import os

def migrate_database():
    db_path = os.path.join('instance', 'grading_app.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if absent column already exists
        cursor.execute("PRAGMA table_info(grade)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'absent' in columns:
            print("Column 'absent' already exists in grade table")
            conn.close()
            return True
        
        # Add the absent column with default value False
        cursor.execute("ALTER TABLE grade ADD COLUMN absent BOOLEAN DEFAULT 0 NOT NULL")
        conn.commit()
        
        print("Successfully added 'absent' column to grade table")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error migrating database: {e}")
        return False

if __name__ == '__main__':
    migrate_database()
