#!/bin/bash

# 1. Automatically create .env from env.h if it exists
if [ -f "env.h" ]; then
    echo "Creating .env from env.h..."
    cp env.h .env
else
    echo "Warning: env.h not found. Using existing .env if present."
fi

# 2. Create the Docker Compose file for DigitalOcean
cat <<EOF > docker-compose.yml
version: '3.8'
services:
  elinity-db:
    image: postgres:15
    container_name: elinity-db
    restart: always
    environment:
      POSTGRES_USER: elinity_user
      POSTGRES_PASSWORD: Deckoviz_prod_2026
      POSTGRES_DB: elinity_db
    ports:
      - "5432:5432"
    volumes:
      - elinity_postgres_data:/var/lib/postgresql/data

  elinity-redis:
    image: redis:7-alpine
    container_name: elinity-redis
    restart: always
    ports:
      - "6379:6379"

  elinity-app:
    build: .
    container_name: elinity-app
    restart: always
    ports:
      - "80:8081" # DigitalOcean will show the app on port 80 (Standard Web Port)
    env_file: .env
    environment:
      - DB_URL=postgresql://elinity_user:Deckoviz_prod_2026@elinity-db:5432/elinity_db
      - REDIS_URL=redis://elinity-redis:6379/0
    command: uvicorn main:app --host 0.0.0.0 --port 8081
    depends_on:
      - elinity-db
      - elinity-redis

volumes:
  elinity_postgres_data:
EOF

# 3. Launch
docker-compose up -d --build

echo "------------------------------------------------"
echo "Elinity P1 is now launching on DigitalOcean!"
echo "Your app will be live on: http://YOUR_DROPLET_IP"
echo "------------------------------------------------"
