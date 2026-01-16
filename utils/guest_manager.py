from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import Tenant, PersonalInfo
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

async def ensure_guest_user(db: AsyncSession, user_id: str):
    """
    Ensures that a user exists with the given ID.
    If not, creates a Guest user.
    Handles concurrency gracefully.
    """
    if not user_id:
        logger.warning("ensure_guest_user called with empty user_id")
        return

    # 1. Check if exists
    logger.info(f"Checking if user {user_id} exists...")
    result = await db.execute(select(Tenant).where(Tenant.id == user_id))
    existing_user = result.scalars().first()
    if existing_user:
        logger.info(f"User {user_id} already exists")
        return # Exists

    # 2. Try to create
    logger.info(f"Creating guest user {user_id}...")
    try:
        guest = Tenant(
            id=user_id,
            email=f"guest_{user_id}@elinity.ai",
            password="guest_password",
            role="user"
        )
        # Fix: Create PersonalInfo to prevent 'NoneType' errors in profile access
        p_info = PersonalInfo(
            tenant=user_id,
            first_name="Guest",
            last_name=user_id[-4:],
            location="Digital Realm"
        )
        
        db.add(guest)
        db.add(p_info)
        await db.commit()
        await db.refresh(guest)
        logger.info(f"✅ Successfully created guest user {user_id}")
    except IntegrityError as e:
        # Race condition: someone else created it
        logger.warning(f"Race condition caught for {user_id}: {e}")
        await db.rollback()
    except Exception as e:
        logger.error(f"❌ Error creating guest user {user_id}: {e}", exc_info=True)
        await db.rollback()
        # Re-raise or handle? If we can't create user, we can't proceed.
        raise e
