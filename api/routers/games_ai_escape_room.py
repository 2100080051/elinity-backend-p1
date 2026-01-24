from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import json
import re
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

GAME_SLUG = 'ai-escape-room'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Cyberpunk Laboratory"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize a new escape room simulation with the theme: {req.theme}. Provide an opening narrative and initial room state."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "You wake up in a cold, metallic room. The air is thin.",
            "room_state": {"name": "Entry Corridor", "lighting": "Dim"},
            "available_actions": ["Search the floor", "Look at the door"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "time_left": 60,
        "inventory": [],
        "room_state": data.get("room_state", {}),
        "puzzles": data.get("puzzles", []),
        "available_actions": data.get("available_actions", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Host"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    CURRENT STATE:
    - Time Left: {s.get('time_left')} mins
    - Inventory: {", ".join(s.get('inventory', []))}
    - Room: {s.get('room_state', {}).get('name')}
    - Active Puzzles: {[p.get('id') for p in s.get('puzzles', []) if p.get('status') == 'active']}
    
    PLAYER ACTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        ai_response = json.loads(resp_str)
    except:
        ai_response = {"narrative": "The room remains silent.", "room_state": s.get("room_state")}

    # Metadata Parsing
    narrative = ai_response.get("narrative", "")
    new_time = s.get("time_left", 60)
    new_inv = list(s.get("inventory", []))
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("time"):
                try: new_time = max(0, new_time + int(re.search(r'[-+]?\d+', up).group()))
                except: pass
            elif up.startswith("item+"):
                new_inv.append(up[5:])
            elif up.startswith("item-"):
                it = up[5:]
                if it in new_inv: new_inv.remove(it)

    new_state = {
        **s,
        "scene": narrative,
        "time_left": new_time,
        "inventory": new_inv,
        "room_state": ai_response.get("room_state", s.get("room_state")),
        "puzzles": ai_response.get("puzzles", s.get("puzzles")),
        "available_actions": ai_response.get("available_actions", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_time <= 0:
        new_state["status"] = "failed"
        new_state["scene"] += "\n\nTIME EXPIRED. THE SIMULATION HAS TERMINATED."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players, 'history': session.history}
