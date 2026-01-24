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

GAME_SLUG = 'ai-inner-world-quest'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Garden of Quiet Reflection"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Internal Horizon with theme: {req.theme}. Present the first terrain and emotion."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "You open your eyes within. A vast horizon stretches out, shaped by your breath.",
            "psyche_data": {"clarity_level": 20, "active_emotion": "Curiosity", "current_terrain": "The Void"},
            "available_moves": ["Breath deeply", "Look around"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "clarity": 20,
        "emotion": data.get("psyche_data", {}).get("active_emotion", "Curiosity"),
        "terrain": data.get("psyche_data", {}).get("current_terrain", "The Void"),
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Seeker"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    PSYCHE STATE:
    - Clarity Level: {s.get('clarity')}% | Active Emotion: {s.get('emotion')}
    - Current Terrain: {s.get('terrain')}
    
    SEEKER INTROSPECTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The world flickers. A thought passes like a cloud.", "psyche_data": s.get('psyche_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_clarity = s.get("clarity", 20)
    new_emotion = s.get("emotion", "Curiosity")
    new_terrain = s.get("terrain", "The Void")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("clarity"):
                try: new_clarity = min(100, max(0, new_clarity + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("emotion"):
                new_emotion = up[8:]
            elif up.startswith("terrain"):
                new_terrain = up[8:]

    new_state = {
        **s,
        "scene": narrative,
        "clarity": new_clarity,
        "emotion": new_emotion,
        "terrain": new_terrain,
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_clarity >= 100:
        new_state["status"] = "awakened"
        new_state["scene"] += "\n\nTOTAL CLARITY ACHIEVED. YOU ARE THE ARCHITECT OF YOUR OWN HORIZON."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
