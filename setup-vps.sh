#!/bin/bash

# ============================================
# Setup script for fresh Hostinger VPS
# ============================================
# شغل السكريبت ده مرة واحدة على VPS جديد

set -e

echo "🚀 Setting up Hostinger VPS for Smart Offer..."

# 1. تحديث النظام
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. تثبيت أدوات أساسية
echo "📦 Installing essential packages..."
sudo apt install -y curl wget git ufw

# 3. تثبيت Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm -f get-docker.sh
    echo "✅ Docker installed. Log out and back in for group changes."
fi

# 4. تثبيت Docker Compose Plugin
echo "🐳 Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    sudo apt install -y docker-compose-plugin
fi

# 5. إعداد Firewall (UFW)
echo "🔥 Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

# 6. إنشاء مجلد المشروع
echo "📁 Creating application directory..."
sudo mkdir -p /docker/smartoffer
sudo chown $USER:$USER /docker/smartoffer

echo ""
echo "✅ VPS setup completed!"
echo ""
echo "⚠️  IMPORTANT: If this is your first time installing Docker, please log out and log back in"
echo "   to apply the docker group changes."
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Clone your repository:"
echo "   cd /docker/smartoffer"
echo "   git clone https://github.com/hamdyadam97/Smartoffer.git ."
echo ""
echo "2. Create environment file:"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "3. Update these variables in .env:"
echo "   - SECRET_KEY (generate a strong random key)"
echo "   - ALLOWED_HOSTS (your domain or server IP)"
echo "   - CSRF_TRUSTED_ORIGINS (https://your-domain.com)"
echo "   - DB_PASSWORD (strong database password)"
echo "   - ADMIN_EMAIL and ADMIN_PASSWORD"
echo ""
echo "4. Follow the deployment steps in DEPLOYMENT.md"
echo ""
