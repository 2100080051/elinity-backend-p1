#!/bin/bash
echo "🚀 Starting Quick Deployment (Supabase Mode)..."

# 1. Pull Code
git pull origin main

# 2. Check Password
if grep -q "\[YOUR-PASSWORD\]" .env; then
    echo "⚠️  Please update .env with your Supabase password first!"
    exit 1
fi

# 3. Stop Old Database Container (Cleanup)
sudo docker stop elinity-db-final 2>/dev/null
sudo docker rm elinity-db-final 2>/dev/null

# 4. Restart Services
sudo docker-compose down
sudo docker-compose up -d --build

# 5. Migrate
echo "🔄 Running Migrations..."
sleep 5
sudo docker exec elinity-app-final alembic upgrade head

echo "✅ Ready!"
