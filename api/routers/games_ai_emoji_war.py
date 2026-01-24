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

GAME_SLUG = 'elinity-ai-emoji-war'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Neo-Tokyo Glitch"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Emoji War arena with theme: {req.theme}. Identify the opposition and narrate the intro."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The arena hums with static. Your opponent, Glitch-King 👑, steps forward.",
            "battle_stats": {"round": 1, "glitch_percent": 0},
            "entities": [{"name": "Glitch-King", "hp": 100, "status": "Ready"}],
            "available_moves": ["⚔️ Strike", "🛡️ Block"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "glitch_percent": 0,
        "hp": 100,
        "round": 1,
        "entities": data.get("entities", []),
        "available_moves": data.get("available_moves", []),
        "faction": "None",
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
    CURRENT ARENA STATE:
    - Player HP: {s.get('hp')}
    - Glitch Meter: {s.get('glitch_percent')}%
    - Faction: {s.get('faction')}
    - Opponents: {s.get('entities')}
    
    GLYPH INPUT: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The attack dissipates into white noise.", "battle_stats": s.get("battle_stats")}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_hp = s.get("hp", 100)
    new_glitch = s.get("glitch_percent", 0)
    new_faction = s.get("faction", "None")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("hp"):
                try: new_hp = min(100, max(0, new_hp + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("glitch"):
                try: new_glitch = min(100, max(0, new_glitch + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("faction+"):
                new_faction = up[8:]

    new_state = {
        **s,
        "scene": narrative,
        "hp": new_hp,
        "glitch_percent": new_glitch,
        "faction": new_faction,
        "entities": data.get("entities", s.get("entities")),
        "available_moves": data.get("available_moves", []),
        "round": s.get("round", 1) + 1,
        "turn": s.get("turn", 0) + 1
    }
    
    if new_hp <= 0:
        new_state["status"] = "defeated"
        new_state["scene"] += "\n\nCRITICAL SYSTEM FAILURE. YOUR GLYPH HAS EXPIRED."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
