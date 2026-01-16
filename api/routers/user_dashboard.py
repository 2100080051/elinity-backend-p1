from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from models.user import Tenant
from models.social import Event
from utils.token import get_current_user
from typing import Dict, Any

# Note: Using prefix in main.py, so this is relative
router = APIRouter(tags=["Dashboard"])

@router.get("/relationship", response_model=Dict[str, Any])
async def get_relationship_dashboard(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Aggregate data for the Relationship Dashboard."""
    # MVP: Fetch upcoming events and basic user info.
    from models.social import Event
    from models.tools import GoalRitual, Nudge
    
    upcoming_events = db.query(Event).filter(Event.host_id == current_user.id).limit(5).all()
    
    # Get active relationship rituals (streaks)
    rituals = db.query(GoalRitual).filter(
        GoalRitual.tenant == current_user.id,
        GoalRitual.is_active == True
    ).all()
    
    # Get recent nudges
    nudges = db.query(Nudge).filter(
        Nudge.tenant == current_user.id,
        Nudge.is_read == False
    ).limit(3).all()
    
    return {
        "status": current_user.personal_info.relationship_status if current_user.personal_info else "Single",
        "upcoming_events": [{"title": e.title, "date": e.start_time} for e in upcoming_events],
        "streaks": [{"title": r.title, "count": r.streak_count} for r in rituals],
        "recent_nudges": [{"content": n.content, "type": n.type} for n in nudges],
        "mood": "AI Analysis Pending",
        "suggestion": "Check out the new social events!",
        "daily_card_preview": "Tap to see your Daily Relationship Insight"
    }

@router.get("/relationship/daily-card", response_model=Dict[str, Any])
async def get_daily_relationship_card(current_user: Tenant = Depends(get_current_user)):
    """Get a daily AI-generated relationship card/prompt."""
    from api.routers._llm import safe_chat_completion
    
    prompt = (
        f"You are a relationship expert. Generate a 'Daily Relationship Card' for a user. "
        f"The card should include: \n"
        f"1) An 'Insight of the Day' (short wisdom)\n"
        f"2) A 'Micro-Action' (something small to do today for their relationship)\n"
        f"3) A 'Conversation Starter' (a deep question for their partner)\n"
        f"Return ONLY a JSON object with keys: insight, action, question."
    )
    
    try:
        resp = await safe_chat_completion(system="You are an AI Relationship Coach.", user_prompt=prompt)
        import json
        card = json.loads(resp)
    except Exception:
        card = {
            "insight": "Small gestures build lasting foundations.",
            "action": "Send a 'thinking of you' text today.",
            "question": "What is one dream you've never shared with me?"
        }
        
    return {"daily_card": card}

@router.get("/me", response_model=Dict[str, Any])
async def get_personal_dashboard(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Aggregate data for the Personal Dashboard."""
    # Lazy import to avoid circulars
    from models.tools import GoalRitual
    from models.journal import Journal
    
    active_rituals_count = db.query(GoalRitual).filter(
        GoalRitual.tenant == current_user.id, 
        GoalRitual.is_active == True
    ).count()
    
    journal_count = db.query(Journal).filter(Journal.tenant == current_user.id).count()
    
    return {
        "quote_of_the_day": "Believe you can and you're halfway there.", # Keeps simple
        "active_rituals": active_rituals_count,
        "journal_count": journal_count, # Renamed from streak to count for accuracy
        "journal_streak": journal_count # Legacy field fallback
    }
