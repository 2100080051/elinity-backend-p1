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

GAME_SLUG = 'ai-social-labyrinth'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Gilded Gala"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Labyrinth with theme: {req.theme}. Present the first social trial."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The doors open. A room full of masks turns toward you. The game begins.",
            "labyrinth_data": {"social_standing": 10, "active_agenda": "Observation", "current_circle": "The Outer Ring"},
            "available_moves": ["Accept a glass", "Scan the crowd"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "standing": 10,
        "agenda": data.get("labyrinth_data", {}).get("active_agenda", "Observation"),
        "circle": data.get("labyrinth_data", {}).get("current_circle", "The Outer Ring"),
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Strategist"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    LABYRINTH STATE:
    - Social Standing: {s.get('standing')} | Active Agenda: {s.get('agenda')}
    - Current Circle: {s.get('circle')}
    
    STRATEGIST GAMBIT: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "A social faux pas! The room grows cold.", "labyrinth_data": s.get('labyrinth_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_standing = s.get("standing", 10)
    new_agenda = s.get("agenda", "Observation")
    new_circle = s.get("circle", "The Outer Ring")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("standing"):
                try: new_standing = min(100, max(0, new_standing + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("agenda"):
                new_agenda = up[7:]
            elif up.startswith("circle"):
                new_circle = up[7:]

    new_state = {
        **s,
        "scene": narrative,
        "standing": new_standing,
        "agenda": new_agenda,
        "circle": new_circle,
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_standing >= 100:
        new_state["status"] = "ascended"
        new_state["scene"] += "\n\nYOU HAVE ACQUIRED UNTOUCHABLE SOCIAL SUPREMACY. THE LABYRINTH IS YOURS."
    elif new_standing <= 0:
        new_state["status"] = "exiled"
        new_state["scene"] += "\n\nSOCIAL EXILE. YOU HAVE BEEN CAST OUT OF THE CIRCLE."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
