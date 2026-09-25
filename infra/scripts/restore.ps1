# ==============================================================================
# Enterprise LMS - Multi-Database Disaster Recovery & Restore Script (PowerShell)
# Restores PostgreSQL (pg_restore), MongoDB (mongorestore), and Redis
# ==============================================================================

param (
    [Parameter(Mandatory=$true)]
    [string]$BackupDir
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BackupDir)) {
    Write-Error "Error: Backup directory $BackupDir does not exist."
    exit 1
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Enterprise LMS Restore from: $BackupDir" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Restore PostgreSQL
$pgFile = Get-ChildItem -Path $BackupDir -Filter "postgres_*.dump" | Select-Object -First 1
if ($pgFile) {
    Write-Host "[1/3] Restoring PostgreSQL from $($pgFile.FullName)..." -ForegroundColor Yellow
    docker cp "$($pgFile.FullName)" lms_prod_postgres:/tmp/restore.dump
    docker exec lms_prod_postgres pg_restore -U lms_user -d lms_db --clean --if-exists -v /tmp/restore.dump
    docker exec lms_prod_postgres rm /tmp/restore.dump
    Write-Host "PostgreSQL restore complete." -ForegroundColor Green
} else {
    Write-Host "Warning: No PostgreSQL dump found in $BackupDir, skipping." -ForegroundColor Yellow
}

# 2. Restore MongoDB
$mongoFile = Get-ChildItem -Path $BackupDir -Filter "mongo_*.archive" | Select-Object -First 1
if ($mongoFile) {
    Write-Host "[2/3] Restoring MongoDB from $($mongoFile.FullName)..." -ForegroundColor Yellow
    docker cp "$($mongoFile.FullName)" lms_prod_mongodb:/tmp/restore.archive
    docker exec lms_prod_mongodb mongorestore --username mongo_admin --password mongo_secure_pass_2026 --authenticationDatabase admin --archive=/tmp/restore.archive --gzip --drop
    docker exec lms_prod_mongodb rm /tmp/restore.archive
    Write-Host "MongoDB restore complete." -ForegroundColor Green
} else {
    Write-Host "Warning: No MongoDB archive found in $BackupDir, skipping." -ForegroundColor Yellow
}

# 3. Restore Redis
$redisFile = Get-ChildItem -Path $BackupDir -Filter "redis_*.rdb" | Select-Object -First 1
if ($redisFile) {
    Write-Host "[3/3] Restoring Redis snapshot from $($redisFile.FullName)..." -ForegroundColor Yellow
    docker stop lms_prod_redis
    docker cp "$($redisFile.FullName)" lms_prod_redis:/data/dump.rdb
    docker start lms_prod_redis
    Write-Host "Redis restore complete." -ForegroundColor Green
} else {
    Write-Host "Warning: No Redis snapshot found in $BackupDir, skipping." -ForegroundColor Yellow
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Enterprise LMS Multi-Database Restore Completed!" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
