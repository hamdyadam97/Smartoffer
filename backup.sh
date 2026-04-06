#!/bin/bash

# Backup script for database and media files

BACKUP_DIR="/opt/backups/smartoffer"
DATE=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="smartoffer-db-1"

mkdir -p $BACKUP_DIR

echo "🔄 Creating backup..."

# Backup database
echo "💾 Backing up database..."
docker exec $DB_CONTAINER pg_dump -U postgres smartoffer > $BACKUP_DIR/db_backup_$DATE.sql

# Backup media files
echo "📁 Backing up media files..."
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz ./media/

# Keep only last 7 backups
echo "🧹 Cleaning old backups..."
cd $BACKUP_DIR
ls -t db_backup_*.sql | tail -n +8 | xargs -r rm
ls -t media_backup_*.tar.gz | tail -n +8 | xargs -r rm

echo "✅ Backup completed: $BACKUP_DIR"
