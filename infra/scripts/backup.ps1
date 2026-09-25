# ==============================================================================
# Enterprise LMS - Automated Multi-Database Backup Script (PowerShell)
# Backs up PostgreSQL (pg_dump), MongoDB (mongodump), and Redis (RDB snapshot)
# ==============================================================================

param (
    [string]$BackupDir = "./backups"
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$targetDir = Join-Path $BackupDir $timestamp

if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Enterprise LMS Backup: $timestamp" -ForegroundColor Cyan
Write-Host "Target Directory: $targetDir" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. PostgreSQL Backup
Write-Host "[1/3] Backing up PostgreSQL Database..." -ForegroundColor Yellow
docker exec lms_prod_postgres pg_dump -U lms_user -d lms_db -F c -b -v -f "/tmp/pg_backup_$timestamp.dump"
docker cp "lms_prod_postgres:/tmp/pg_backup_$timestamp.dump" "$targetDir/postgres_$timestamp.dump"
docker exec lms_prod_postgres rm "/tmp/pg_backup_$timestamp.dump"
Write-Host "PostgreSQL backup completed: $targetDir/postgres_$timestamp.dump" -ForegroundColor Green

# 2. MongoDB Backup
Write-Host "[2/3] Backing up MongoDB Content Collections..." -ForegroundColor Yellow
docker exec lms_prod_mongodb mongodump --username mongo_admin --password mongo_secure_pass_2026 --authenticationDatabase admin --db lms_content_db --archive="/tmp/mongo_backup_$timestamp.archive" --gzip
docker cp "lms_prod_mongodb:/tmp/mongo_backup_$timestamp.archive" "$targetDir/mongo_$timestamp.archive"
docker exec lms_prod_mongodb rm "/tmp/mongo_backup_$timestamp.archive"
Write-Host "MongoDB backup completed: $targetDir/mongo_$timestamp.archive" -ForegroundColor Green

# 3. Redis Snapshot Backup
Write-Host "[3/3] Backing up Redis Key-Value Store..." -ForegroundColor Yellow
docker exec lms_prod_redis redis-cli -a redis_secure_pass_2026 bgsave
Start-Sleep -Seconds 2
docker cp "lms_prod_redis:/data/dump.rdb" "$targetDir/redis_$timestamp.rdb"
Write-Host "Redis snapshot backup completed: $targetDir/redis_$timestamp.rdb" -ForegroundColor Green

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Enterprise LMS Backup Finished Successfully!" -ForegroundColor Cyan
Write-Host "Artifacts saved to: $targetDir" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
