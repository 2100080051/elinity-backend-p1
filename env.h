# SUPABASE CONNECTION (External Managed DB)
# Replace [YOUR-PASSWORD] with Nikshith2906#
DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.franwuowlrcddwmhbhjo.supabase.co:5432/postgres
DB_SSL_MODE=require

# LEGACY DOCKER DB (Disabled)
# DB_HOST=db
# DB_PORT=5432
# DB_NAME=elinity_db
# DB_USER=elinity_user
# DB_PASSWORD=Deckoviz_prod_2026
# DB_URL=postgresql://elinity_user:Deckoviz_prod_2026@db:5432/elinity_db

# REDIS SETTINGS (GCP Internal Docker)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# MILVUS SETTINGS (GCP Internal Docker)
MILVUS_URI=http://milvus:19530

# MONGODB (External/Atlas - as per your backup)
MONGO_DB_URL=mongodb+srv://2100080051aids_db_user:2dckMkQtZ7ZuxCkp@cluster0.telxnft.mongodb.net/personas?retryWrites=true&w=majority

# CELERY / RABBITMQ (External/CloudAMQP - as per your backup)
CELERY_BROKER_URL=amqps://rrqnywgt:YOUfCZu-6O9AMJbPmAJEjnVNNMgnVDoD@duck.lmq.cloudamqp.com/rrqnywgt

# APP SETTINGS
ENV=production
DEBUG=False
PYTHONPATH=/app
APP_NAME=elinity-backend-p1
SECRET_KEY=supersecretkey123
CORS_ALLOW_ORIGINS=https://elinity-premium-games.vercel.app,http://localhost:3000,http://localhost:5173


# API KEYS
OPENROUTER_API_KEY=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
GOOGLE_API_KEY=AIzaSyCmjxkn42I8ALSzvDef21gU6DrhZ5t3dcc
ELEVENLABS_API_KEY=sk_ceb0f0fa4094d89c64c9181d5f531fbaef50a54819141d56
ASSEMBLYAI_API_KEY=e61cbe314d084a83868ea6786bc2f3d2
PINECONE_API_KEY=pcsk_4zsmH9_Pc7Le3Cra2LB2JmZcKitxrmkH962wYrqgShVrDu6ZVarK2yZEq8hy9diVsrBV57
