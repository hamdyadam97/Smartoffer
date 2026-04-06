#!/bin/bash

# Setup script for fresh VPS

set -e

echo "🚀 Setting up VPS for Smart Offer..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create app directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/smartoffer
cd /opt/smartoffer

# Clone repository (you'll need to update this with your repo)
echo "📥 Cloning repository..."
# git clone https://github.com/yourusername/smartoffer.git .

echo ""
echo "⚠️  IMPORTANT: Please complete the following steps manually:"
echo ""
echo "1. Clone your repository to /opt/smartoffer"
echo "2. Create .env file: cp .env.example .env && nano .env"
echo "3. Update all environment variables in .env file"
echo "4. Run: docker-compose up -d"
echo "5. Create superuser: docker-compose exec backend python manage.py createsuperuser"
echo ""
echo "📖 For SSL setup, run: certbot --nginx -d your-domain.com"
echo ""
echo "✅ Setup script completed!"
