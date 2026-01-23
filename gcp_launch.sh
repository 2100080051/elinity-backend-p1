#!/bin/bash

# =================================================================
# ELINITY P1 - GCP GOOGLE CLOUD DEPLOYMENT (Port 80)
# =================================================================

# 1. Update and Install Docker (If not already present)
echo "📦 Checking for Docker..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker and Docker-Compose..."
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
else
    echo "✅ Docker is already installed."
fi

# 2. Environment Setup
echo "📝 Setting up environment..."
if [ -f "env.h" ]; then
    cp env.h .env
else
    echo "❌ ERROR: env.h not found!"
    exit 1
fi

# 3. Check for Password Placeholder
if grep -q "\[YOUR-PASSWORD\]" .env; then
    echo "⚠️  SUPABASE PASSWORD REQUIRED!"
    read -sp "Enter Supabase DB Password: " DB_PASS
    echo ""
    # Use different delimiter for sed to avoid issues with # in password
    sed -i "s|\[YOUR-PASSWORD\]|$DB_PASS|g" .env
fi

# 4. Generate Docker Compose (No local DB, uses Supabase)
echo "🔧 Generating GCP Docker Config..."
cat <<EOF > docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    container_name: elinity-gcp-redis
    restart: always
    ports:
      - "6379:6379"

  elinity-app:
    build: .
    container_name: elinity-gcp-app
    restart: always
    ports:
      - "80:8081"
    env_file: .env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - REDIS_HOST=redis
    command: uvicorn main:app --host 0.0.0.0 --port 8081
    depends_on:
      - redis
EOF

# 5. Cleanup Previous GCP Containers
echo "🧹 Cleaning up old containers..."
sudo docker stop elinity-gcp-app elinity-gcp-redis 2>/dev/null
sudo docker rm elinity-gcp-app elinity-gcp-redis 2>/dev/null

# 6. Build and Launch
echo "🚀 Launching Elinity on GCP (Port 80)..."
sudo docker-compose up -d --build

# 7. Database Migration
echo "🔄 Running Supabase Migrations..."
sleep 5
sudo docker exec elinity-gcp-app alembic upgrade head

echo "------------------------------------------------"
echo "✅ Elinity P1 is now LIVE on Google Cloud!"
echo "📡 Connected to Supabase External DB"
echo "🌍 URL: http://YOUR_GCP_EXTERNAL_IP"
echo "📄 Docs: http://YOUR_GCP_EXTERNAL_IP/docs"
echo "------------------------------------------------"
