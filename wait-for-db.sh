#!/bin/sh
# wait-for-db.sh

set -e

# This script waits for the database to be ready by repeatedly trying to connect.
# It uses environment variables that are standard in Railway's Postgres service.

until pg_isready -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec "$@"
