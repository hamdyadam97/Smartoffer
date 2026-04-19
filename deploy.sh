#!/bin/bash
set -e

echo "========================================"
echo "  Smart Offer - Simple Deploy Script   "
echo "========================================"

cd "$(dirname "$0")"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "[1/6] Pulling latest code..."
git pull origin main

echo "[2/6] Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "[3/6] Integrating frontend with Django..."
python3 build-frontend.py

echo "[4/6] Running migrations..."
python3 manage.py migrate --noinput

echo "[5/6] Collecting static files..."
python3 manage.py collectstatic --noinput

echo "[6/6] Restarting Gunicorn..."
sudo systemctl restart gunicorn-smartoffer

echo ""
echo "========================================"
echo "  Deployed successfully!               "
echo "========================================"
