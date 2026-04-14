#!/bin/bash

# Backup script for database and media files
set -e

# Detect docker compose command
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

BACKUP_DIR="/opt/backups/smartoffer"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "🔄 Creating backup..."

# Get database container name dynamically
DB_CONTAINER=$(${COMPOSE_CMD} ps -q db)

if [ -z "$DB_CONTAINER" ]; then
    echo "❌ Database container not found. Make sure the app is running."
    exit 1
fi

# Backup database
echo "💾 Backing up database..."
docker exec $DB_CONTAINER pg_dump -U postgres smartoffer > $BACKUP_DIR/db_backup_$DATE.sql

# Backup media files
echo "📁 Backing up media files..."
if [ -d "./media" ]; then
    tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz ./media/
else
    echo "⚠️  No media directory found, skipping media backup"
fi

# Keep only last 7 backups
echo "🧹 Cleaning old backups..."
cd $BACKUP_DIR
ls -t db_backup_*.sql 2>/dev/null | tail -n +8 | xargs -r rm
ls -t media_backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm

echo "✅ Backup completed: $BACKUP_DIR"
