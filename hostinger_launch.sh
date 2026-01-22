#!/bin/bash

# =================================================================
# ELINITY V3 - LIGHTWEIGHT SUPABASE DEPLOYMENT
# =================================================================

# 1. Environment Setup
echo "📝 Setting up environment..."
if [ -f "env.h" ]; then
    cp env.h .env
else
    echo "❌ ERROR: env.h not found!"
    exit 1
fi

# 2. Check for Password Placeholder
if grep -q "\[YOUR-PASSWORD\]" .env; then
    echo "⚠️  PASSWORD REQUIRED!"
    read -sp "Enter your Supabase Database Password: " DB_PASS
    echo ""
    # Replace placeholder in .env
    sed -i "s/\[YOUR-PASSWORD\]/$DB_PASS/g" .env
fi

# 3. Generate Minimal Docker Compose (No Database Container!)
echo "🔧 Generating Minimal Docker Config..."
cat <<EOF > docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    container_name: elinity-redis-final
    restart: always
    ports:
      - "6390:6379"

  elinity-app:
    build: .
    container_name: elinity-app-final
    restart: always
    ports:
      - "8090:8081"
    env_file: .env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - REDIS_HOST=redis
    command: uvicorn main:app --host 0.0.0.0 --port 8081
    depends_on:
      - redis
EOF

# 4. Stop Old Containers (Graceful Attempt)
echo "🛑 Stopping old containers..."
sudo docker stop elinity-app-final elinity-redis-final elinity-db-final 2>/dev/null
sudo docker rm elinity-app-final elinity-redis-final elinity-db-final 2>/dev/null

# 5. Build and Launch
echo "🚀 Building and Launching (App + Redis)..."
sudo docker-compose up -d --build

# 6. Database Migration (Using App Container)
echo "🔄 Running Database Upgrade (Alembic)..."
sleep 5
sudo docker exec elinity-app-final alembic upgrade head

echo "------------------------------------------------"
echo "✅ Elinity V3 is LIVE (Port 8090)!"
echo "📡 Connected to Supabase External DB"
echo "📄 Docs: http://YOUR_IP:8090/docs"
echo "------------------------------------------------"
