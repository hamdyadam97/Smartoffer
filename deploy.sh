#!/bin/bash

# ============================================
# Deploy script for Smart Offer on Hostinger VPS
# ============================================
# ده السكريبت اللي بيعمل النشر. بيشتغل تلقائي من GitHub Actions،
# وممكن تشغله يدوي على السيرفر.

set -e

# اتأكد إن docker compose متاح
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

echo "🚀 Starting deployment..."

# اتأكد إنك في المجلد الصح
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Run this script from /docker/smartoffer"
    exit 1
fi

# ============================================
# 1. بناء الفرونت (Build Frontend)
# ============================================
# بنستخدم Docker image فيها Node.js عشان نبني React app
# مش محتاجين نثبت Node.js على السيرفر نفسه

echo "📦 Building frontend..."
docker run --rm \
    -v "$(pwd)/frontend:/app" \
    -w /app \
    node:20-alpine \
    sh -c "npm ci && npm run build"

# ============================================
# 2. إيقاف الـ Containers القديمة
# ============================================
echo "🐳 Stopping old containers..."
${COMPOSE_CMD} down

# ============================================
# 3. بناء و تشغيل الـ Containers الجديدة
# ============================================
echo "🐳 Building and starting new containers..."
${COMPOSE_CMD} up -d --build

# ============================================
# 4. تشغيل Migrations
# ============================================
echo "🔄 Running database migrations..."
${COMPOSE_CMD} exec -T backend python manage.py migrate --noinput

# ============================================
# 5. تجميع Static Files
# ============================================
echo "📁 Collecting static files..."
${COMPOSE_CMD} exec -T backend python manage.py collectstatic --noinput

# ============================================
# 6. تنظيف الصور القديمة
# ============================================
echo "🧹 Cleaning up old Docker images..."
docker system prune -f

# ============================================
# 7. انتهى
# ============================================
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Check status:  ${COMPOSE_CMD} ps"
echo "📝 Backend logs:  ${COMPOSE_CMD} logs -f backend"
echo "📝 Nginx logs:    ${COMPOSE_CMD} logs -f nginx"
echo ""
echo "🌐 Your app should be accessible at:"
echo "   http://smartoffer.m3had-system.cloud"
echo "   http://${SERVER_IP}:8080"
