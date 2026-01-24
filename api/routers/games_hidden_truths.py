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

GAME_SLUG = 'ai-hidden-truths'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Shattered Archive"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Chamber of Veiled Realities with theme: {req.theme}. Present the first layer."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "A shimmering veil of data blocks the path. The truth is buried deep.",
            "truth_data": {"depth_meters": 0, "current_layer": "The Surface", "revelations_found": 0},
            "available_moves": ["Scan the surface", "Touch the veil"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "depth": 0,
        "layer": data.get("truth_data", {}).get("current_layer", "The Surface"),
        "revelations": 0,
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Excavator"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    EXCAVATION STATE:
    - Discovery Depth: {s.get('depth')}m | Revelations Found: {s.get('revelations')}
    - Current Layer: {s.get('layer')}
    
    EXCAVATOR DIG: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The ground is hard. Progress is slow.", "truth_data": s.get('truth_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_depth = s.get("depth", 0)
    new_revelations = s.get("revelations", 0)
    new_layer = s.get("layer", "The Surface")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("depth"):
                try: new_depth = min(100, max(0, new_depth + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("revelation"):
                try: new_revelations += int(re.search(r'[-+]?\d+', up).group())
                except: pass
            elif up.startswith("layer"):
                new_layer = up[5:]

    new_state = {
        **s,
        "scene": narrative,
        "depth": new_depth,
        "revelations": new_revelations,
        "layer": new_layer,
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_depth >= 100:
        new_state["status"] = "uncovered"
        new_state["scene"] += "\n\nTHE CORE TRUTH HAS BEEN EXHUMED. THE ARCHIVE IS COMPLETE."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
