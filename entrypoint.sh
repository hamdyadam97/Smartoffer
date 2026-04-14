#!/bin/sh

set -e

# Wait for database using Python (no external nc needed)
echo "Waiting for database..."
python -c "
import socket
import time
while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('db', 5432))
        s.close()
        break
    except socket.error:
        time.sleep(1)
"
echo "Database is ready!"

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if not exists
echo "Creating superuser if needed..."
python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartoffer_django.settings')
django.setup()

from accounts.models import Person

admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

if not Person.objects.filter(email=admin_email).exists():
    Person.objects.create_superuser(
        email=admin_email,
        password=admin_password,
        first_name='Admin',
        forth_name='User'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn smartoffer_django.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
