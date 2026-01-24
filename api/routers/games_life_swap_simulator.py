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

GAME_SLUG = 'ai-life-swap'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Corporate Titan"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Life Exchange with theme: {req.theme}. Present the first scenario."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "You wake up in a life that isn't yours. The coffee is expensive, and everyone expects you to know what to do.",
            "swap_data": {"sync_level": 50, "current_persona": req.theme, "persona_status": "Stable"},
            "available_actions": ["Check the calendar", "Look in the mirror"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "sync": 50,
        "persona": data.get("swap_data", {}).get("current_persona", req.theme),
        "status": "active",
        "moves": data.get("available_actions", []),
        "available_actions": data.get("available_actions", []),
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Proxy"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    EXCHANGE STATE:
    - Sync Level: {s.get('sync')}% | Persona: {s.get('persona')}
    
    PROXY ACTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The mask slips. Someone is looking at you weirdly.", "swap_data": s.get('swap_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_sync = s.get("sync", 50)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("sync"):
                try: new_sync = min(100, max(0, new_sync + int(re.search(r'[-+]?\d+', up).group())))
                except: pass

    new_state = {
        **s,
        "scene": narrative,
        "sync": new_sync,
        "moves": data.get("available_actions", []),
        "available_actions": data.get("available_actions", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_sync >= 100:
        new_state["status"] = "integrated"
        new_state["scene"] += "\n\nTOTAL INTEGRATION. THIS LIFE IS NOW YOURS."
    elif new_sync <= 0:
        new_state["status"] = "expelled"
        new_state["scene"] += "\n\nTHE MASK HAS FALLEN. YOU HAVE BEEN EXPELLED FROM THE EXCHANGE."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
