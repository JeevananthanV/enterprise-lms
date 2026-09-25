#!/bin/bash
# ==============================================================================
# Enterprise LMS - Multi-Database Disaster Recovery & Restore Script
# Restores PostgreSQL (pg_restore), MongoDB (mongorestore), and Redis
# ==============================================================================

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path_to_backup_directory>"
    echo "Example: $0 ./backups/20260912_120000"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "${BACKUP_DIR}" ]; then
    echo "Error: Backup directory ${BACKUP_DIR} does not exist."
    exit 1
fi

echo "========================================================"
echo "Starting Enterprise LMS Restore from: ${BACKUP_DIR}"
echo "========================================================"

# 1. Restore PostgreSQL
PG_FILE=$(find "${BACKUP_DIR}" -name "postgres_*.dump" | head -n 1)
if [ -n "${PG_FILE}" ]; then
    echo "[1/3] Restoring PostgreSQL from ${PG_FILE}..."
    docker cp "${PG_FILE}" lms_prod_postgres:/tmp/restore.dump
    docker exec lms_prod_postgres pg_restore -U "${POSTGRES_USER:-lms_user}" -d "${POSTGRES_DB:-lms_db}" --clean --if-exists -v /tmp/restore.dump || true
    docker exec lms_prod_postgres rm /tmp/restore.dump
    echo "PostgreSQL restore complete."
else
    echo "Warning: No PostgreSQL dump found in ${BACKUP_DIR}, skipping."
fi

# 2. Restore MongoDB
MONGO_FILE=$(find "${BACKUP_DIR}" -name "mongo_*.archive" | head -n 1)
if [ -n "${MONGO_FILE}" ]; then
    echo "[2/3] Restoring MongoDB from ${MONGO_FILE}..."
    docker cp "${MONGO_FILE}" lms_prod_mongodb:/tmp/restore.archive
    docker exec lms_prod_mongodb mongorestore --username "${MONGO_INITDB_ROOT_USERNAME:-mongo_admin}" --password "${MONGO_INITDB_ROOT_PASSWORD:-mongo_secure_pass_2026}" --authenticationDatabase admin --archive=/tmp/restore.archive --gzip --drop
    docker exec lms_prod_mongodb rm /tmp/restore.archive
    echo "MongoDB restore complete."
else
    echo "Warning: No MongoDB archive found in ${BACKUP_DIR}, skipping."
fi

# 3. Restore Redis
REDIS_FILE=$(find "${BACKUP_DIR}" -name "redis_*.rdb" | head -n 1)
if [ -n "${REDIS_FILE}" ]; then
    echo "[3/3] Restoring Redis snapshot from ${REDIS_FILE}..."
    docker stop lms_prod_redis
    docker cp "${REDIS_FILE}" lms_prod_redis:/data/dump.rdb
    docker start lms_prod_redis
    echo "Redis restore complete."
else
    echo "Warning: No Redis snapshot found in ${BACKUP_DIR}, skipping."
fi

echo "========================================================"
echo "Enterprise LMS Multi-Database Restore Completed!"
echo "========================================================"
