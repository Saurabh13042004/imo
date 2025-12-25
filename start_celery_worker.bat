@echo off
REM Celery Worker Startup Script for Windows
REM This script starts the Celery worker for processing async review tasks

setlocal enabledelayedexpansion

set WORKER_NAME=review-worker-1
set LOGLEVEL=info
set CONCURRENCY=4
set QUEUES=default,reviews,high

echo.
echo ===================================
echo Starting Celery Worker
echo ===================================
echo Worker Name: %WORKER_NAME%
echo Log Level: %LOGLEVEL%
echo Concurrency: %CONCURRENCY%
echo Queues: %QUEUES%
echo.

cd backend

REM Check if Redis is running
echo Checking Redis connection...
python -c "^
import redis^
import os^
from app.config import settings^
try:^
    redis_url = settings.REDIS_URL or 'redis://localhost:6379/0'^
    r = redis.from_url(redis_url)^
    r.ping()^
    print('Redis is running and accessible')^
except Exception as e:^
    print(f'Redis connection failed: {e}')^
    exit(1)^
"

if %ERRORLEVEL% neq 0 (
    echo Redis connection failed. Make sure Redis is running.
    pause
    exit /b 1
)

echo.
echo Starting worker...
echo.

celery -A app.celery_app worker ^
    --loglevel=%LOGLEVEL% ^
    --concurrency=%CONCURRENCY% ^
    --queues=%QUEUES% ^
    --hostname=%WORKER_NAME%@%%h ^
    --time-limit=1800 ^
    --soft-time-limit=1500 ^
    --without-gossip ^
    --without-mingle ^
    --without-heartbeat ^
    -O fair

pause
