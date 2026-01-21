#!/bin/bash

# 1. Update and Install Docker (GCP Ubuntu doesn't come with it pre-installed)
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# 2. Automatically create .env from env.h if it exists
if [ -f "env.h" ]; then
    echo "Creating .env from env.h..."
    cp env.h .env
else
    echo "Warning: env.h not found. Using existing .env if present."
fi

# 3. Create the Docker Compose file for GCP
cat <<EOF > docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    container_name: elinity-db-gcp
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
    container_name: elinity-redis-gcp
    restart: always
    ports:
      - "6379:6379"

  elinity-app:
    build: .
    container_name: elinity-app-gcp
    restart: always
    ports:
      - "80:8081" # GCP will show the app on port 80 (Standard Web Port)
    env_file: .env
    environment:
      - DB_URL=postgresql://elinity_user:Deckoviz_prod_2026@db:5432/elinity_db
      - REDIS_URL=redis://redis:6379/0
    command: uvicorn main:app --host 0.0.0.0 --port 8081
    depends_on:
      - db
      - redis

volumes:
  elinity_gcp_data:
EOF

# 4. Launch
sudo docker-compose up -d --build

echo "------------------------------------------------"
echo "Elinity P1 is now launching on Google Cloud!"
echo "Your app will be live on: http://YOUR_GCP_VM_IP"
echo "------------------------------------------------"
