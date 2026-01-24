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

GAME_SLUG = 'ai-character-swap'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Shattered Mirror"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Hall of Reflections with theme: {req.theme}. Present the first form."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The mirror ripples. A shape begins to form. Is it you, or something else?",
            "identity_data": {"sync_level": 10, "active_trait": "Unknown", "current_form": "The Shadow"},
            "available_morphs": ["Touch the glass", "Stare into the void"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "sync": 10,
        "trait": data.get("identity_data", {}).get("active_trait", "Unknown"),
        "form": data.get("identity_data", {}).get("current_form", "The Shadow"),
        "morphs": data.get("available_morphs", []),
        "available_actions": data.get("available_morphs", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Vessel"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    IDENTITY STATE:
    - Sync Level: {s.get('sync')}% | Active Trait: {s.get('trait')}
    - Current Form: {s.get('form')}
    
    VESSEL MOVEMENT: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The reflection cracks. Identity instability detected.", "identity_data": s.get('identity_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_sync = s.get("sync", 10)
    new_trait = s.get("trait", "Unknown")
    new_form = s.get("form", "The Shadow")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("sync"):
                try: new_sync = min(100, max(0, new_sync + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("trait"):
                new_trait = up[6:]
            elif up.startswith("form"):
                new_form = up[5:]

    new_state = {
        **s,
        "scene": narrative,
        "sync": new_sync,
        "trait": new_trait,
        "form": new_form,
        "morphs": data.get("available_morphs", []),
        "available_actions": data.get("available_morphs", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_sync >= 100:
        new_state["status"] = "merged"
        new_state["scene"] += "\n\nTOTAL SYNCHRONIZATION ACHIEVED. YOU ARE NO LONGER THE VESSEL; YOU ARE THE FORM."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
