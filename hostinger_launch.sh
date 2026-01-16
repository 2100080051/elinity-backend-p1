#!/bin/bash

# 1. Automatically create .env from env.h if it exists
if [ -f "env.h" ]; then
    echo "Creating .env from env.h..."
    cp env.h .env
else
    echo "Warning: env.h not found. Using existing .env if present."
fi

# 2. Create the Docker Compose file automatically
# UPDATED PORTS: Public 8082 -> Container 8085
cat <<EOF > docker-compose.yml
version: '3.8'
services:
  elinity-p1-db:
    image: postgres:15
    container_name: elinity-p1-db
    restart: always
    environment:
      POSTGRES_USER: elinity_user
      POSTGRES_PASSWORD: Deckoviz_prod_2026
      POSTGRES_DB: elinity_db
    ports:
      - "5435:5432"
    volumes:
      - elinity_p1_data:/var/lib/postgresql/data

  elinity-p1-redis:
    image: redis:7-alpine
    container_name: elinity-p1-redis
    restart: always
    ports:
      - "6385:6379"

  elinity-p1-app:
    build: .
    container_name: elinity-p1-app
    restart: always
    ports:
      - "8082:8085"
    env_file: .env
    environment:
      - DB_URL=postgresql://elinity_user:Deckoviz_prod_2026@elinity-p1-db:5432/elinity_db
      - REDIS_URL=redis://elinity-p1-redis:6379/0
    command: uvicorn main:app --host 0.0.0.0 --port 8085
    depends_on:
      - elinity-p1-db
      - elinity-p1-redis

volumes:
  elinity_p1_data:
EOF

# 3. Build and Launch
sudo docker-compose up -d --build

echo "------------------------------------------------"
echo "Elinity P1 Backend is now launching on port 8082"
echo "------------------------------------------------"
