#!/usr/bin/env bash
# StoneWalker PostgreSQL backup script
# Install: cp backup.sh /opt/stonewalker/backup.sh && chmod +x /opt/stonewalker/backup.sh
# Cron:    echo "0 3 * * * stonewalker /opt/stonewalker/backup.sh" > /etc/cron.d/stonewalker-backup

set -euo pipefail

BACKUP_DIR="/opt/stonewalker/backups"
DB_NAME="stonewalker"
DB_USER="stonewalker"
RETENTION_DAYS=14
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

# Dump and compress
pg_dump -U "$DB_USER" -d "$DB_NAME" --format=custom --compress=6 \
    --file="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump" 2>/dev/null

# Also create a plain SQL backup (useful for disaster recovery)
pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE" 2>/dev/null

# Verify the backup is non-empty
if [ ! -s "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file is empty: $BACKUP_FILE" >&2
    exit 1
fi

# Also back up media files (QR codes, profile pics, stone images)
MEDIA_BACKUP="${BACKUP_DIR}/media_${TIMESTAMP}.tar.gz"
tar -czf "$MEDIA_BACKUP" -C /opt/stonewalker/source/content media/ 2>/dev/null || true

# Remove old backups
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find "$BACKUP_DIR" -name "${DB_NAME}_*.dump" -mtime +${RETENTION_DAYS} -delete
find "$BACKUP_DIR" -name "media_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup complete: $BACKUP_FILE"
