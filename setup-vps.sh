#!/bin/bash

# Setup script for fresh Hostinger VPS (Ubuntu 22.04/24.04)
set -e

echo "🚀 Setting up Hostinger VPS for Smart Offer..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "📦 Installing essential packages..."
sudo apt install -y curl wget git ufw

# Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm -f get-docker.sh
    echo "✅ Docker installed. You may need to log out and back in for group changes to take effect."
fi

# Install Docker Compose Plugin
echo "🐳 Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    sudo apt install -y docker-compose-plugin
fi

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Create app directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/smartoffer
sudo chown $USER:$USER /opt/smartoffer

echo ""
echo "✅ VPS setup completed!"
echo ""
echo "⚠️  IMPORTANT: If this is your first time installing Docker, please log out and log back in"
echo "   to apply the docker group changes, then continue with the deployment steps."
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Clone your repository:"
echo "   cd /opt/smartoffer"
echo "   git clone https://github.com/YOUR_USERNAME/smartoffer.git ."
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
echo "4. Deploy the application:"
echo "   ./deploy.sh"
echo ""
echo "5. (Optional) Setup SSL with Certbot:"
echo "   docker run -it --rm \\"
echo "     -v /opt/smartoffer/certbot/conf:/etc/letsencrypt \\"
echo "     -v /opt/smartoffer/certbot/www:/var/www/certbot \\"
echo "     -p 80:80 \\"
echo "     certbot/certbot certonly --standalone -d your-domain.com"
echo ""
