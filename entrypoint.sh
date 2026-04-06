#!/bin/sh

# Wait for database
while ! nc -z db 5432; do
  echo "Waiting for database..."
  sleep 1
done

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if not exists
echo "Creating superuser..."
python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartoffer_django.settings')
django.setup()

from accounts.models import Person

if not Person.objects.filter(email=os.getenv('ADMIN_EMAIL', 'admin@example.com')).exists():
    Person.objects.create_superuser(
        email=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
        password=os.getenv('ADMIN_PASSWORD', 'admin123'),
        first_name='Admin',
        forth_name='User'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Start nginx
echo "Starting nginx..."
service nginx start

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn smartoffer_django.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
