#!/bin/sh
set -e

if [ "$POSTGRES_DB" ]
then
    echo "Waiting for postgres..."
    python waitfordb.py
fi


echo "Creating tables..."
python create_tables.py

echo "Starting server..."
exec "$@"