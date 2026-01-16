import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret"
JWT_HASH_ALGORITHM = os.getenv("JWT_HASH_ALGORITHM") or "HS256"

# Safe int parsing with sensible defaults so missing envs don't crash imports.
def _int_env(name: str, default: int) -> int:
    v = os.getenv(name)
    try:
        return int(v) if v is not None else default
    except Exception:
        return default

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = _int_env("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
JWT_REFRESH_TOKEN_EXPIRE_DAYS = _int_env("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7)
HASH_ALGORITHM = os.getenv("HASH_ALGORITHM") or "bcrypt"

GOOGLE_APPLICATION_CREDENTIALS=os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCS_BUCKET_NAME=os.getenv("GCS_BUCKET_NAME")

# Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = _int_env("REDIS_PORT", 6379)
REDIS_DB = _int_env("REDIS_DB", 0)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# PostgreSQL Database connection
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER','') }:{os.getenv('DB_PASSWORD','')}"
    f"@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}/{os.getenv('DB_NAME','') }"
)

# Ensure SSL for managed Postgres hosts (Render, AWS RDS, etc.). If a local DB is used,
# leaving sslmode off is fine. We prefer setting sslmode=require when the host is not
# localhost to avoid "SSL connection has been closed unexpectedly" errors during startup.
db_host = os.getenv('DB_HOST', '')
if db_host and not db_host.startswith(('localhost', '127.', '::1', 'postgres', 'db', 'host.docker.internal')):
    if 'sslmode' not in DATABASE_URL:
        # Append sslmode=require if not already present
        if '?' in DATABASE_URL:
            DATABASE_URL = DATABASE_URL + '&sslmode=require'
        else:
            DATABASE_URL = DATABASE_URL + '?sslmode=require'
