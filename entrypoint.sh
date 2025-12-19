#!/bin/sh
set -e

if [ "$POSTGRES_DB" ]
then
    echo "Waiting for postgres..."
    python waitfordb.py
fi

# Run migrations
echo "Making migrations..."
python manage.py makemigrations core
echo "Running migrations..."
python manage.py migrate

# Create superuser if variables are defined
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser creation failed or already exists (ignoring)"
fi

echo "Starting server..."
exec "$@"