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

GAME_SLUG = 'ai-creative-duel'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Cyber-Colosseum"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Arena with theme: {req.theme}. Announce the first round."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "WELCOME TO THE ARENA! The crowd is hungry for brilliance. Who will strike first?",
            "duel_data": {"style_points": 0, "hype_level": 50, "creative_health": 100},
            "available_moves": ["Step into the light", "Scan the opponent"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "style": 0,
        "hype": 50,
        "health": 100,
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Gladiator"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    ARENA STATE:
    - Style Points: {s.get('style')} | Hype Level: {s.get('hype')}%
    - Creative Health: {s.get('health')}%
    
    GLADIATOR ATTACK: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "A sloppy move! The crowd booes.", "duel_data": s.get('duel_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_style = s.get("style", 0)
    new_hype = s.get("hype", 50)
    new_health = s.get("health", 100)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("style"):
                try: new_style = min(1000, max(0, new_style + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("hype"):
                try: new_hype = min(100, max(0, new_hype + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("health"):
                try: new_health = min(100, max(0, new_health + int(re.search(r'[-+]?\d+', up).group())))
                except: pass

    new_state = {
        **s,
        "scene": narrative,
        "style": new_style,
        "hype": new_hype,
        "health": new_health,
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_health <= 0:
        new_state["status"] = "eliminated"
        new_state["scene"] += "\n\nK.O.! YOU HAVE BEEN ELIMINATED FROM THE ARENA. BETTER LUCK NEXT INCIDENT."
    elif new_style >= 500:
        new_state["status"] = "legendary"
        new_state["scene"] += "\n\nLEGENDARY PERFORMANCE! THE ARBITER HAS DECLARED YOU THE ABSOLUTE CHAMPION."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
