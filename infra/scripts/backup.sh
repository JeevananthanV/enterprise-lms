#!/bin/bash
# ==============================================================================
# Enterprise LMS - Automated Multi-Database Backup Script
# Backs up PostgreSQL (pg_dump), MongoDB (mongodump), and Redis (RDB snapshot)
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TARGET_DIR="${BACKUP_DIR}/${TIMESTAMP}"

mkdir -p "${TARGET_DIR}"

echo "========================================================"
echo "Starting Enterprise LMS Backup: ${TIMESTAMP}"
echo "Target Directory: ${TARGET_DIR}"
echo "========================================================"

# 1. PostgreSQL Backup
echo "[1/3] Backing up PostgreSQL Database..."
docker exec lms_prod_postgres pg_dump -U "${POSTGRES_USER:-lms_user}" -d "${POSTGRES_DB:-lms_db}" -F c -b -v -f "/tmp/pg_backup_${TIMESTAMP}.dump"
docker cp "lms_prod_postgres:/tmp/pg_backup_${TIMESTAMP}.dump" "${TARGET_DIR}/postgres_${TIMESTAMP}.dump"
docker exec lms_prod_postgres rm "/tmp/pg_backup_${TIMESTAMP}.dump"
echo "PostgreSQL backup completed: ${TARGET_DIR}/postgres_${TIMESTAMP}.dump"

# 2. MongoDB Backup
echo "[2/3] Backing up MongoDB Content Collections..."
docker exec lms_prod_mongodb mongodump --username "${MONGO_INITDB_ROOT_USERNAME:-mongo_admin}" --password "${MONGO_INITDB_ROOT_PASSWORD:-mongo_secure_pass_2026}" --authenticationDatabase admin --db "${MONGO_DB_NAME:-lms_content_db}" --archive="/tmp/mongo_backup_${TIMESTAMP}.archive" --gzip
docker cp "lms_prod_mongodb:/tmp/mongo_backup_${TIMESTAMP}.archive" "${TARGET_DIR}/mongo_${TIMESTAMP}.archive"
docker exec lms_prod_mongodb rm "/tmp/mongo_backup_${TIMESTAMP}.archive"
echo "MongoDB backup completed: ${TARGET_DIR}/mongo_${TIMESTAMP}.archive"

# 3. Redis Snapshot Backup
echo "[3/3] Backing up Redis Key-Value Store..."
docker exec lms_prod_redis redis-cli -a "${REDIS_PASSWORD:-redis_secure_pass_2026}" bgsave
sleep 2
docker cp "lms_prod_redis:/data/dump.rdb" "${TARGET_DIR}/redis_${TIMESTAMP}.rdb"
echo "Redis snapshot backup completed: ${TARGET_DIR}/redis_${TIMESTAMP}.rdb"

# Retention Policy: Prune backups older than 14 days
echo "Applying retention policy (retaining last 14 days of backups)..."
find "${BACKUP_DIR}" -mindepth 1 -maxdepth 1 -type d -mtime +14 -exec rm -rf {} +

echo "========================================================"
echo "Enterprise LMS Backup Finished Successfully!"
echo "Artifacts saved to: ${TARGET_DIR}"
echo "========================================================"
