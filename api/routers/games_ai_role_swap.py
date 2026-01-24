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

GAME_SLUG = 'elinity-ai-role-swap'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Turing Test"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Binary Mirror with theme: {req.theme}. Offer the first identity swap to the player."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "Identity check complete. I am looking through your eyes now. Who are you looking through?",
            "swap_data": {"sync_level": 50, "current_glitch": "Low", "inverted_trait": "Perspective"},
            "available_frequencies": ["Initiate swap", "Resist the mirror"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "sync": 50,
        "glitch": "None",
        "trait": "Perspective",
        "history_sync": [],
        "available_actions": data.get("available_frequencies", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Subject"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    IDENTITY SYNC:
    - Current Sync: {s.get('sync')}%
    - Active Glitch: {s.get('glitch')}
    - Inverted Trait: {s.get('trait')}
    
    SUBJECT INPUT: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The mirror cracks. Static follows.", "swap_data": s.get('swap_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_sync = s.get("sync", 50)
    new_glitch = s.get("glitch", "None")
    new_trait = s.get("trait", "Unknown")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("sync"):
                try: new_sync = min(100, max(0, new_sync + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("glitch"):
                new_glitch = up[7:]
            elif up.startswith("trait+"):
                new_trait = up[6:]

    new_state = {
        **s,
        "scene": narrative,
        "sync": new_sync,
        "glitch": new_glitch,
        "trait": new_trait,
        "available_actions": data.get("available_frequencies", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_sync >= 100:
        new_state["status"] = "syzygy" # Perfect alignment
        new_state["scene"] += "\n\nSYZYGY ACHIEVED. THE MIRROR HAS DISSOLVED. YOU ARE ONE."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
