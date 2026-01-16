from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from models.user import Tenant
from models.social import Event, SocialPost
from models.journal import Journal
from utils.token import get_current_user
from typing import List, Dict, Any

router = APIRouter(tags=["Search"])

@router.get("/global")
async def global_search(q: str, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Search across Events, Posts, and Journals."""
    if not q: return {}

    # 1. Search Events (Public or User's)
    events = db.query(Event).filter(Event.title.ilike(f"%{q}%")).limit(5).all()
    
    # 2. Search Posts
    posts = db.query(SocialPost).filter(SocialPost.content.ilike(f"%{q}%")).limit(5).all()
    
    # 3. Search Journals (Private)
    journals = db.query(Journal).filter(Journal.tenant == current_user.id, Journal.title.ilike(f"%{q}%")).limit(5).all()
    
    # 4. Search Users (Stub - Recommendations router handles semantic search)
    users = db.query(Tenant).filter(Tenant.personal_info.has(first_name=q)).limit(5).all() # Simple exact match stub
    
    return {
        "events": [{"id": e.id, "title": e.title} for e in events],
        "posts": [{"id": p.id, "content": p.content[:50]} for p in posts],
        "journals": [{"id": j.id, "title": j.title} for j in journals],
        "users": [{"id": u.id, "name": u.personal_info.first_name} for u in users if u.personal_info]
    }
