#!/bin/sh
set -e

if [ "$POSTGRES_DB" ]
then
    echo "Waiting for postgres..."
    python scripts/waitfordb.py
fi


echo "Creating tables..."
python scripts/create_tables.py

echo "Starting server..."
exec "$@"