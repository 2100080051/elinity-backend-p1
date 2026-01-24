#!/bin/bash
# Local Test Script - Mimics Production Exactly

echo "🧪 Starting Local Docker Test..."

# 1. Setup Env
if [ ! -f .env ]; then
    cp env.h .env
    echo "⚠️  Created .env from env.h"
fi

# 2. Ask for Password if missing
if grep -q "\[YOUR-PASSWORD\]" .env; then
    echo "🔑 We need your Supabase Password for the test:"
    read -sp "Password: " DB_PASS
    echo ""
    sed -i "s/\[YOUR-PASSWORD\]/$DB_PASS/g" .env
fi

# 3. Generate Docker Compose for Local Test
# Note: Using localhost ports 8081 and 6379 locally
cat <<EOF > docker-compose.local-test.yml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    container_name: elinity-local-redis
    ports:
      - "6379:6379"

  elinity-app:
    build: .
    container_name: elinity-local-app
    ports:
      - "8081:8081"
    env_file: .env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - REDIS_HOST=redis
    command: uvicorn main:app --host 0.0.0.0 --port 8081 --reload
    depends_on:
      - redis
EOF

# 4. cleanup
docker stop elinity-local-app elinity-local-redis 2>/dev/null
docker rm elinity-local-app elinity-local-redis 2>/dev/null

# 5. Run
echo "🚀 Launching via Docker..."
docker-compose -f docker-compose.local-test.yml up --build
