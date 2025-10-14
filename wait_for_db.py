import os
import time
import psycopg2
import sys

def wait_for_db():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL environment variable not set.", file=sys.stderr)
        sys.exit(1)

    # Ensure the URL is in the format psycopg2 expects
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    print("Waiting for database...")
    retries = 30
    while retries > 0:
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            print("Database is ready!")
            return
        except psycopg2.OperationalError as e:
            print(f"Database not ready, sleeping... (Error: {e})")
            retries -= 1
            time.sleep(2)

    print("Timed out waiting for the database.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    wait_for_db()
