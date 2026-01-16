from typing import Optional
from fastapi import Header, HTTPException, status
import os
from datetime import datetime


def _extract_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None


async def require_service_key(authorization: Optional[str] = Header(None)) -> dict:
    """Validate Authorization: Bearer <service_key> against MongoDB `service_keys` collection.

    Returns the matching service key document (dict) on success, raises 401 on failure.
    """
    token = _extract_bearer(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing service key")

    mongo_url = os.environ.get('MONGO_DB_URL')
    if not mongo_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="MONGO_DB_URL not configured")

    try:
        # import pymongo lazily (avoid failing import if package not present)
        from pymongo import MongoClient
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="pymongo not installed on server")

    try:
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=3000)
        db = client.get_default_database()
        coll = db.get_collection('service_keys')
        docs = list(coll.find({}))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to query service keys")

    try:
        from utils.token import pwd_context
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server hashing context unavailable")

    for d in docs:
        try:
            if pwd_context.verify(token, d.get('key_hash', '')):
                return d
        except Exception:
            continue

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid service key")
