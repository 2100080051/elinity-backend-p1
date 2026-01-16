from sqlalchemy.ext.asyncio import AsyncSession
from models.activity import UserActivity
from typing import Dict, Any, Optional
import datetime

async def log_user_activity(
    db: AsyncSession, 
    user_id: str, 
    activity_type: str, 
    target_id: Optional[str] = None, 
    details: Dict[str, Any] = None
):
    """
    Logs a user activity to the database asynchronously.
    """
    if details is None:
        details = {}
        
    try:
        activity = UserActivity(
            tenant_id=user_id,
            activity_type=activity_type,
            target_id=str(target_id) if target_id else None,
            details=details,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(activity)
        await db.commit()
    except Exception as e:
        # We don't want to crash the main request if logging fails, 
        # but we should at least print the error.
        print(f"FAILED TO LOG ACTIVITY: {e}")
