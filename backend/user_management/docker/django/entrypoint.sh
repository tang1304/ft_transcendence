#!/bin/sh

# Wait for the database to be ready
echo "Waiting for database..."
echo "Host: $SQL_HOST"
echo "Port: $SQL_PORT"
while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done
echo "Database ready"

#python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input --clear
python manage.py createsuperuser --noinput

#exec "gunicorn" "user_management.wsgi.application" "--bind" "0.0.0.0:8000"
exec "$@"