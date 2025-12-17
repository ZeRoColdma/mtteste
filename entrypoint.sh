#!/bin/sh
set -e

if [ "$POSTGRES_DB" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations
echo "Making migrations..."
python manage.py makemigrations
echo "Running migrations..."
python manage.py migrate

# Create superuser if variables are defined
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser creation failed or already exists (ignoring)"
fi

echo "Starting server..."
exec "$@"