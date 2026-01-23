#!/bin/bash

# =================================================================
# ELINITY P1 - GCP GOOGLE CLOUD DEPLOYMENT (Local Postgres)
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
    echo "Warning: env.h not found. Using existing .env if present."
fi

# 3. Create the Docker Compose file for GCP (Including Local DB)
echo "🔧 Generating GCP Docker Config (Local DB)..."
cat <<EOF > docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    container_name: elinity-gcp-db
    restart: always
    environment:
      POSTGRES_USER: elinity_user
      POSTGRES_PASSWORD: Deckoviz_prod_2026
      POSTGRES_DB: elinity_db
    ports:
      - "5432:5432"
    volumes:
      - elinity_gcp_data:/var/lib/postgresql/data

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
      - DATABASE_URL=postgresql://elinity_user:Deckoviz_prod_2026@db:5432/elinity_db
      - REDIS_URL=redis://redis:6379/0
      - REDIS_HOST=redis
    command: uvicorn main:app --host 0.0.0.0 --port 8081
    depends_on:
      - db
      - redis

volumes:
  elinity_gcp_data:
EOF

# 4. Cleanup Previous GCP Containers
echo "🧹 Cleaning up old containers..."
sudo docker stop elinity-gcp-app elinity-gcp-redis elinity-gcp-db 2>/dev/null
sudo docker rm elinity-gcp-app elinity-gcp-redis elinity-gcp-db 2>/dev/null

# 5. Build and Launch
echo "🚀 Launching Elinity on GCP (Port 80)..."
sudo docker-compose up -d --build

# 6. Database Migration
echo "🔄 Running Local Migrations..."
sleep 10
sudo docker exec elinity-gcp-app alembic upgrade head

echo "------------------------------------------------"
echo "✅ Elinity P1 is now LIVE on Google Cloud!"
echo "📡 Connected to LOCAL PostgreSQL Container"
echo "🌍 URL: http://YOUR_GCP_EXTERNAL_IP"
echo "📄 Docs: http://YOUR_GCP_EXTERNAL_IP/docs"
echo "------------------------------------------------"
