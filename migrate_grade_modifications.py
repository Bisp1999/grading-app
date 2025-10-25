"""Migration to add grade modification tracking columns.

This migration:
1. Adds 5 new columns to the Grade table
2. Backfills original_grade and original_absent from existing data
"""

from app import create_app, db
from app.models import Grade
from sqlalchemy import text

def upgrade():
    """Add new columns and backfill data."""
    app = create_app()
    with app.app_context():
        print("Starting migration: add_grade_modification_tracking")
        
        # Step 1: Add new columns
        print("Adding new columns to grade table...")
        with db.engine.connect() as conn:
            # Add original_grade column
            conn.execute(text("ALTER TABLE grade ADD COLUMN original_grade FLOAT"))
            # Add original_absent column
            conn.execute(text("ALTER TABLE grade ADD COLUMN original_absent BOOLEAN"))
            # Add modification_type column
            conn.execute(text("ALTER TABLE grade ADD COLUMN modification_type VARCHAR(50)"))
            # Add modification_notes column
            conn.execute(text("ALTER TABLE grade ADD COLUMN modification_notes TEXT"))
            # Add modified_at column
            conn.execute(text("ALTER TABLE grade ADD COLUMN modified_at DATETIME"))
            conn.commit()
        
        print("New columns added successfully.")
        
        # Step 2: Backfill original values from current values
        print("Backfilling original values from existing data...")
        grades = Grade.query.all()
        count = 0
        for grade in grades:
            grade.original_grade = grade.grade
            grade.original_absent = grade.absent
            count += 1
            if count % 100 == 0:
                print(f"  Processed {count} grades...")
        
        db.session.commit()
        print(f"Backfilled {count} grade records.")
        print("Migration completed successfully!")

def downgrade():
    """Remove the new columns."""
    app = create_app()
    with app.app_context():
        print("Starting rollback: add_grade_modification_tracking")
        
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE grade DROP COLUMN original_grade"))
            conn.execute(text("ALTER TABLE grade DROP COLUMN original_absent"))
            conn.execute(text("ALTER TABLE grade DROP COLUMN modification_type"))
            conn.execute(text("ALTER TABLE grade DROP COLUMN modification_notes"))
            conn.execute(text("ALTER TABLE grade DROP COLUMN modified_at"))
            conn.commit()
        
        print("Rollback completed successfully!")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()