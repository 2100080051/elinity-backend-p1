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

GAME_SLUG = 'elinity-ai-rap-battle'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Underground Subway"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Open the Rap Arena with theme: {req.theme}. Introduce the opponent and set the stage in verse."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "Welcome to the pit, where the weak get split.\nI'm the Master of the Core, you ready for war?",
            "battle_data": {"flow_score": 0, "hype_level": 10},
            "arena_state": {"location": "Subway Station", "lights": "Dim Blue"},
            "available_lines": ["Mic check 1-2", "Drop the beat"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "flow": 0,
        "hype": 10,
        "round": 1,
        "arena": data.get("arena_state", {}),
        "available_actions": data.get("available_lines", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "MC"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    ARENA STATUS:
    - Round: {s.get('round')} | Location: {s.get('arena', {}).get('location')}
    - Flow State: {s.get('flow')}%
    - Crowd Hype: {s.get('hype')}%
    
    MC VERSE: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The crowd goes silent. Your mic is dead.", "battle_data": {"flow_score": s.get('flow'), "hype_level": s.get('hype')}}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_flow = s.get("flow", 0)
    new_hype = s.get("hype", 10)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("flow"):
                try: new_flow = min(100, max(0, new_flow + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("hype"):
                try: new_hype = min(100, max(0, new_hype + int(re.search(r'[-+]?\d+', up).group())))
                except: pass

    new_state = {
        **s,
        "scene": narrative,
        "flow": new_flow,
        "hype": new_hype,
        "arena": data.get("arena_state", s.get("arena")),
        "available_actions": data.get("available_lines", []),
        "round": s.get("round", 1) + 1,
        "turn": s.get("turn", 0) + 1
    }
    
    if new_hype >= 100:
        new_state["status"] = "vanguard" # Win state
        new_state["scene"] += "\n\nTHE CROWD DISINTEGRATES INTO PURE ENERGY. YOU ARE THE VANGUARD."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
