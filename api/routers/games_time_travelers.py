from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import re
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

GAME_SLUG = 'ai-time-travelers'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Victorian Nexus"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Temporal Weave with theme: {req.theme}. Present the first era and anomaly."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The gears of time grind as you materialize. A new history awaits your touch.",
            "time_data": {"temporal_stability": 100, "current_era": "Unknown", "butterfly_points": 0},
            "available_actions": ["Adjust the dial", "Step out of the rift"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "stability": 100,
        "era": data.get("time_data", {}).get("current_era", "Unknown"),
        "points": 0,
        "actions": data.get("available_actions", []),
        "available_actions": data.get("available_actions", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Traveler"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    TEMPORAL STATE:
    - Stability: {s.get('stability')}% | Butterfly Points: {s.get('points')}
    - Current Era: {s.get('era')}
    
    TRAVELER ACTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "A temporal loop has formed! Paradox imminent.", "time_data": s.get('time_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_stability = s.get("stability", 100)
    new_points = s.get("points", 0)
    new_era = s.get("era", "Unknown")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("stability"):
                try: new_stability = min(100, max(0, new_stability + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("points"):
                try: new_points = max(0, new_points + int(re.search(r'[-+]?\d+', up).group()))
                except: pass
            elif up.startswith("era"):
                new_era = up[4:]

    new_state = {
        **s,
        "scene": narrative,
        "stability": new_stability,
        "points": new_points,
        "era": new_era,
        "actions": data.get("available_actions", []),
        "available_actions": data.get("available_actions", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_stability <= 0:
        new_state["status"] = "collapsed"
        new_state["scene"] += "\n\nTHE TIMELINE HAS COLLAPSED. PARADOX CONSUMED ALL."
    elif new_points >= 2000:
        new_state["status"] = "legendary"
        new_state["scene"] += "\n\nYOU HAVE SHAPED THE ULTIMATE HISTORY. THE WEAVE IS PERMANENT."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
