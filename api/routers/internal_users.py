from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional
from database.session import get_db
from sqlalchemy.orm import Session
from models.user import Tenant
from auth.service_key_checker import require_service_key

router = APIRouter(prefix="/internal", tags=["internal"])


def _extract_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None


# The service key dependency is now provided by `auth.service_key_checker.require_service_key`


@router.get("/users/{user_id}")
async def get_user_by_id(user_id: str, svc_key: dict = Depends(require_service_key), db: Session = Depends(get_db)):
    """Return a full user profile by id. Accessible only to callers with a valid service key.

    This endpoint intentionally does not return an admin user for the service key — it returns
    the requested user's profile.
    """
    user = db.query(Tenant).filter(Tenant.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Return the SQLAlchemy model object; FastAPI's Pydantic response models (if used) will handle serialization
    return user
