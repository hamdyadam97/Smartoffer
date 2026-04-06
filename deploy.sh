#!/bin/bash

# Deploy script for VPS

set -e

echo "🚀 Starting deployment..."

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build and start containers
echo "🐳 Building and starting containers..."
docker-compose down
docker-compose pull
docker-compose up -d --build

# Run migrations
echo "🔄 Running migrations..."
docker-compose exec -T backend python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec -T backend python manage.py collectstatic --noinput

# Clean up
echo "🧹 Cleaning up..."
docker system prune -f

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Check status: docker-compose ps"
echo "📝 View logs: docker-compose logs -f"
