from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from jose import jwt, JWTError
from typing import Optional
from fastapi import Depends, HTTPException, status
from database.session import get_db, Session, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import Tenant
from utils.settings import (
    SECRET_KEY,
    JWT_HASH_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    HASH_ALGORITHM
)
 
# Security utils
_scheme = HASH_ALGORITHM or 'bcrypt'
pwd_context = CryptContext(schemes=[_scheme], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",  
    scopes={"me": "Read current user's profile"}  
)


def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Generate an access token with specified expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)

def verify_access_token(token: str, db: Session) -> Optional[Tenant]:
    """Verify the access token and return the user if valid"""
    
    if not token:
        return None
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_HASH_ALGORITHM])
        user_id = payload.get("sub") 
        if not user_id:
            return None
        # Get user from database
        user = db.query(Tenant).filter(Tenant.id == user_id).first()
        if not user:
            return None
        return user
    except jwt.JWTError as e: 
        return None
async def verify_access_token_async(token: str, db: AsyncSession) -> Optional[Tenant]:
    """Async version: Verify the access token and return the user if valid"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_HASH_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        result = await db.execute(select(Tenant).where(Tenant.id == user_id))
        user = result.scalars().first()
        return user
    except jwt.JWTError:
        return None
    except Exception:
        return None


def create_access_from_refresh(refresh_token: str) -> str:
    """Generate an access token from a refresh token."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=JWT_HASH_ALGORITHM)
        return create_access_token({"sub": payload["sub"]})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

def create_refresh_token(data: dict) -> str:
    """Generate a refresh token with longer expiration."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)

async def get_current_user(
    request: Request = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Decode JWT, fetch Tenant, and enforce authentication""" 
    
    # Try to get token from Authorization header first
    if not token and request:
        
        # Fall back to cookie if no Authorization header
        token = request.cookies.get("access_token")
        
        if token and token.startswith("Bearer "):
            token = token[7:]  # Remove 'Bearer ' prefix
            
    
    if not token:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        
        user = verify_access_token(token, db)
        if not user:
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except JWTError as e:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication",
        )

async def get_optional_user(
    request: Request = None,
    db: AsyncSession = Depends(get_async_db)
) -> Optional[Tenant]:
    """
    Like get_current_user but returns None instead of raising 401.
    Used for endpoints that support both authenticated and guest users.
    Works with async database sessions.
    """
    token = None
    
    # Try Authorization header first
    if request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
        
        # Fall back to cookie
        if not token:
            cookie_token = request.cookies.get("access_token")
            if cookie_token and cookie_token.startswith("Bearer "):
                token = cookie_token[7:]
            elif cookie_token:
                token = cookie_token
    
    if not token:
        return None  # No authentication - return None for guest handling
        
    try:
        user = await verify_access_token_async(token, db)
        return user  # Could be None if token invalid
    except Exception:
        return None  # Invalid token - treat as guest


async def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> Tenant:
    """Get current user from access_token cookie"""
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = token[7:]  # Remove 'Bearer ' prefix
    user = verify_access_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user