release: chmod +x ./wait-for-db.sh && ./wait-for-db.sh alembic upgrade head
web: gunicorn --graceful-timeout 60 --timeout 120 run:app
