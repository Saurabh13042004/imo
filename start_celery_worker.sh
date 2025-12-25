#!/bin/bash
# Celery Worker Startup Script
# This script starts the Celery worker for processing async review tasks

# Configuration
WORKER_NAME="review-worker-1"
LOGLEVEL="info"
CONCURRENCY=4  # Number of concurrent worker processes
QUEUES="default,reviews,high"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Celery Worker...${NC}"
echo "Worker Name: $WORKER_NAME"
echo "Log Level: $LOGLEVEL"
echo "Concurrency: $CONCURRENCY"
echo "Queues: $QUEUES"
echo ""

# Ensure we're in the backend directory
cd "$(dirname "$0")/backend" || exit 1

# Check if Redis is running
echo -e "${YELLOW}Checking Redis connection...${NC}"
python -c "
import redis
import os
from app.config import settings

try:
    redis_url = settings.REDIS_URL or 'redis://localhost:6379/0'
    r = redis.from_url(redis_url)
    r.ping()
    print('✓ Redis is running and accessible')
except Exception as e:
    print(f'✗ Redis connection failed: {e}')
    print('Make sure Redis is running on the configured URL')
    exit(1)
" || exit 1

echo ""
echo -e "${GREEN}Starting worker...${NC}"
echo ""

# Start Celery worker
celery -A app.celery_app worker \
    --loglevel=$LOGLEVEL \
    --concurrency=$CONCURRENCY \
    --queues=$QUEUES \
    --hostname=$WORKER_NAME@%h \
    --time-limit=1800 \
    --soft-time-limit=1500 \
    --without-gossip \
    --without-mingle \
    --without-heartbeat \
    -O fair
