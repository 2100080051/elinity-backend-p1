# session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from utils.settings import DATABASE_URL, REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD
import redis

# Async SQLAlchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.orm import sessionmaker as sync_sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker

# Load environment variables
load_dotenv()


# SQLAlchemy (sync) setup - used for metadata.create_all and sync code
engine = create_engine(DATABASE_URL.replace("+asyncpg", ""))
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Async engine and sessionmaker for application async DB operations
# Convert DATABASE_URL to async driver if needed (postgresql+asyncpg)
ASYNC_DATABASE_URL = DATABASE_URL
if DATABASE_URL.startswith("postgresql://") and "asyncpg" not in DATABASE_URL:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if "sslmode" in ASYNC_DATABASE_URL:
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    future=True,
    connect_args={"ssl": "require"} if "azure" in ASYNC_DATABASE_URL or "sslmode" in DATABASE_URL else {}
)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

# PostgreSQL Database dependency (sync)
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

# PostgreSQL Database dependency (async)
async def get_async_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Raw PostgreSQL client connection if needed
def get_client():
    return engine.connect()

# Redis client dependency
def get_redis_client():
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=False  # Keep as bytes to avoid encoding issues
    )
    try:
        yield redis_client
    finally:
        redis_client.close()

# Import models so Alembic/autogenerate sees them when it imports this module
try:
    # Import conversation models to register with Base.metadata
    from models import conversation  # noqa: F401
    from models import question_card  # [NEW] Register model
    from models import game_session # [NEW] Register GameSession
except Exception:
    # If models have heavy dependencies, avoid crashing import-time tools
    pass



