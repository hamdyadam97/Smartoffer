#!/bin/bash
set -e

echo "========================================"
echo "  Smart Offer - VPS Setup (One-time)  "
echo "========================================"

PROJECT_DIR="/var/www/smartoffer"

# 1. Update system
sudo apt update

# 2. Install dependencies
sudo apt install -y python3-pip python3-venv nodejs npm nginx git

# 3. Create project directory
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 4. Clone repo (if not already cloned)
if [ ! -d ".git" ]; then
    git clone https://github.com/hamdyadam97/Smartoffer.git .
fi

# 5. Setup Python venv
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# 6. Setup environment
cp .env.production .env
nano .env  # User edits this

# 7. Build and deploy
./deploy.sh

# 8. Setup systemd service
sudo sed 's|/docker/smartoffer|/var/www/smartoffer|g' gunicorn-smartoffer.service > /etc/systemd/system/gunicorn-smartoffer.service
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-smartoffer
sudo systemctl start gunicorn-smartoffer

# 9. Setup nginx
sudo sed 's|/docker/smartoffer|/var/www/smartoffer|g' nginx-smartoffer.conf > /etc/nginx/sites-available/smartoffer
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/smartoffer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo "========================================"
echo "  Setup complete!                     "
echo "  Visit: http://smartoffer.m3had-system.cloud"
echo "========================================"
