from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database.session import get_db
from models.user import Tenant
from models.connection import Connection
from utils.token import get_current_user
from datetime import datetime, timezone
import logging

router = APIRouter(prefix="/connections", tags=["Connections P1"])
logger = logging.getLogger(__name__)

# --- HELPERS (Adapted from recommendations.py) ---
def calculate_heuristic_score(user_a, user_b):
    """Simple python-based similarity score until Vector DB is fully stable."""
    try:
        score = 0.1 # Base score
        
        # Interests
        a_interests = set(user_a.interests_and_hobbies.interests or []) if user_a.interests_and_hobbies else set()
        b_interests = set(user_b.interests_and_hobbies.interests or []) if user_b.interests_and_hobbies else set()
        
        overlap = len(a_interests.intersection(b_interests))
        if overlap > 0:
            score += min(overlap * 0.2, 0.5) # Max 0.5 from interests
            
        # Location
        a_loc = user_a.personal_info.location.lower() if user_a.personal_info and user_a.personal_info.location else "."
        b_loc = user_b.personal_info.location.lower() if user_b.personal_info and user_b.personal_info.location else ".."
        if a_loc == b_loc:
            score += 0.3
            
        return min(score, 0.99)
    except Exception as e:
        logger.error(f"Scoring error: {e}")
        return 0.1

def generate_ai_insight(user_b, score):
    """Stub for AI explanation."""
    return f"We noticed you share common interests. With a compatibility score of {int(score*100)}%, {user_b.personal_info.first_name} could be a great match."

# --- ENDPOINTS ---

@router.get("/daily/{mode}")
async def get_daily_batch(
    mode: str, 
    current_user: Tenant = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Fetch daily recommendations based on the Founder's P1 logic.
    - Check Quota (3/5/8)
    - Apply Threshold vs Top Pick logic
    - Persist as 'suggested' connections
    """
    prefs = current_user.connection_preferences or {}
    
    # 1. Config
    daily_limit = prefs.get('daily_limit', 3)
    filter_mode = prefs.get('filter_mode', 'threshold') # 'threshold' or 'top_picks'
    min_threshold = prefs.get('min_threshold', 0.60)
    
    # 2. Check Exising Recommendations for TODAY
    # (Simple logic: Count 'suggested' created today)
    # For a real app, we'd check date. For prototype, just check total active suggestions.
    
    existing_recs = db.query(Connection).filter(
        Connection.user_a_id == current_user.id,
        Connection.status == 'suggested',
        Connection.mode == mode
    ).all()
    
    # If we already have a batch, return it
    if len(existing_recs) >= daily_limit:
        return [format_connection(c, db) for c in existing_recs]
        
    # 3. Generate New Recommendations (Fill the gap)
    needed = daily_limit - len(existing_recs)
    
    # Get Candidates (exclude self and already connected)
    existing_ids = [c.user_b_id for c in db.query(Connection).filter(Connection.user_a_id == current_user.id).all()]
    existing_ids.append(current_user.id)
    
    candidates = db.query(Tenant).filter(Tenant.id.notin_(existing_ids)).limit(50).all()
    
    scored = []
    for cand in candidates:
        score = calculate_heuristic_score(current_user, cand)
        scored.append((cand, score))
        
    # 4. Apply Filtering Logic
    scored.sort(key=lambda x: x[1], reverse=True)
    
    final_picks = []
    if filter_mode == 'threshold':
        # Only above N%
        final_picks = [x for x in scored if x[1] >= min_threshold]
        # Just take top 'needed' from those who passed
        final_picks = final_picks[:needed]
    else:
        # Top picks regardless of score
        final_picks = scored[:needed]
        
    # 5. Persist
    new_connections = []
    for cand, score in final_picks:
        conn = Connection(
            user_a_id=current_user.id,
            user_b_id=cand.id,
            mode=mode,
            score=score,
            status='suggested',
            feedback={} # Init
        )
        db.add(conn)
        new_connections.append(conn)
        
    db.commit()
    
    # Refresh to get IDs
    for c in new_connections:
        db.refresh(c)
        
    # Combine old + new
    all_recs = existing_recs + new_connections
    return [format_connection(c, db) for c in all_recs]

@router.post("/action/{connection_id}")
async def handle_connection_action(
    connection_id: str,
    action: str = Body(..., embed=True), # 'accept', 'decline', 'archive'
    feedback: str = Body(None, embed=True),
    reason: str = Body(None, embed=True),
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle user actions on a profile.
    - Accept: Move to 'pending_b' (waiting for other user) or 'matched' if B already accepted A.
    - Decline: Move to 'declined', store AI Feedback.
    - Archive: Move to 'archived'.
    """
    conn = db.query(Connection).filter(Connection.id == connection_id).first()
    if not conn:
        raise HTTPException(404, "Connection not found")
        
    if conn.user_a_id != current_user.id and conn.user_b_id != current_user.id:
        raise HTTPException(403, "Not authorized")
        
    if action == 'archive':
        conn.status = 'archived'
        db.commit()
        return {"ok": True, "status": "archived"}
        
    if action == 'decline':
        conn.status = 'declined'
        conn.feedback = {
            "declined_by": current_user.id,
            "reason": reason,
            "feedback_text": feedback,
            "timestamp": str(datetime.now())
        }
        # TODO: Trigger AI Learning from feedback here
        db.commit()
        return {"ok": True, "status": "declined"}
        
    if action == 'accept':
        # Logic: If I am User A, set to pending_b.
        # If I am User B (and it was pending_b), set to Match.
        
        # Check if reverse connection exists? 
        # For simplicity in this mono-table model:
        # If status is 'suggested' and I am A -> 'pending_b'
        # If status is 'pending_a' and I am B -> 'matched' (Logic depends on who initiated)
        
        # Simpler Logic: 
        # Check if the OTHER person has already 'accepted' (pending_me).
        # Since we create 'suggested' strictly for User A, User B doesn't see it yet.
        # When User A accepts, we must notify User B.
        
        if conn.status == 'suggested':
            conn.status = 'pending_b'
            # TODO: Create a 'suggested' or 'notification' for User B so they see this.
            # Ideally create a mirror connection record or update notification table.
            msg = f"You were suggested to {current_user.personal_info.first_name}, and they accepted."
            # For prototype: Just update status.
            
        elif conn.status == 'pending_b' and conn.user_b_id == current_user.id:
             # Double Opt-In Complete!
             conn.status = 'matched'
             conn.ai_icebreaker = "Make a joke about coffee." # Placeholder
             
        db.commit()
        return {"ok": True, "status": conn.status}

    raise HTTPException(400, "Invalid action")

@router.post("/confirm/{connection_id}")
async def confirm_relationship(
    connection_id: str,
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Moves a match to 'Personal Circle'.
    If mode is 'romantic', this should disable further romantic searches.
    """
    conn = db.query(Connection).filter(Connection.id == connection_id).first()
    if not conn or conn.status != 'matched':
        raise HTTPException(400, "Must be a match first")
        
    conn.status = 'personal_circle'
    
    # If Romantic, turn off search
    if conn.mode == 'romantic':
        prefs = dict(current_user.connection_preferences)
        if 'active_modes' in prefs:
             prefs['active_modes']['romantic'] = False
             current_user.connection_preferences = prefs
             
    db.commit()
    return {"ok": True, "message": "Moved to Personal Circle"}

def format_connection(conn, db):
    # Fetch User B profile
    user_b = db.query(Tenant).filter(Tenant.id == conn.user_b_id).first()
    return {
        "id": conn.id,
        "user_b": {
            "id": user_b.id,
            "name": f"{user_b.personal_info.first_name} {user_b.personal_info.last_name}",
            "location": user_b.personal_info.location,
            # Add other profile fields
        },
        "score": conn.score,
        "mode": conn.mode,
        "status": conn.status,
        "ai_insight": generate_ai_insight(user_b, conn.score)
    }
