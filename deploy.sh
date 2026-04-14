#!/bin/bash

# Deploy script for Hostinger VPS
set -e

# Detect docker compose command
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

echo "🚀 Starting deployment..."

# Ensure we are in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Make sure you run this script from the project root."
    exit 1
fi

# Build frontend using Docker (no need to install Node on host)
echo "📦 Building frontend..."
docker run --rm \
    -v "$(pwd)/frontend:/app" \
    -w /app \
    node:20-alpine \
    sh -c "npm ci && npm run build"

# Stop existing containers
echo "🐳 Stopping existing containers..."
${COMPOSE_CMD} down

# Build and start containers
echo "🐳 Building and starting containers..."
${COMPOSE_CMD} up -d --build

# Run migrations
echo "🔄 Running migrations..."
${COMPOSE_CMD} exec -T backend python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
${COMPOSE_CMD} exec -T backend python manage.py collectstatic --noinput

# Clean up old Docker images
echo "🧹 Cleaning up old Docker images..."
docker system prune -f

# Get server IP for display
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Check status: ${COMPOSE_CMD} ps"
echo "📝 View backend logs: ${COMPOSE_CMD} logs -f backend"
echo "📝 View nginx logs: ${COMPOSE_CMD} logs -f nginx"
echo ""
echo "🌐 Your app should be accessible at:"
echo "   http://${SERVER_IP}"
