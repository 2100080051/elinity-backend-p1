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

GAME_SLUG = 'ai-beast-builder'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Obsidian Hatchery"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Hatchery with theme: {req.theme}. Present the first essence choice."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "A warm egg pulses in the center of the chamber. Life waits to be defined.",
            "beast_data": {"vitality": 10, "resonance": 10, "current_form": "The Egg"},
            "available_essences": ["Infuse warmth", "Listen to the heartbeat"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "vitality": 10,
        "resonance": 10,
        "form": data.get("beast_data", {}).get("current_form", "The Egg"),
        "essences": data.get("available_essences", []),
        "available_actions": data.get("available_essences", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Life-Binder"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    HATCHERY STATE:
    - Vitality: {s.get('vitality')}% | Mythic Resonance: {s.get('resonance')}%
    - Current Form: {s.get('form')}
    
    BINDER WEAVE: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The essence destabilizes. The beast shrieks in pain.", "beast_data": s.get('beast_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_vitality = s.get("vitality", 10)
    new_resonance = s.get("resonance", 10)
    new_form = s.get("form", "The Egg")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("vitality"):
                try: new_vitality = min(100, max(0, new_vitality + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("resonance"):
                try: new_resonance = min(100, max(0, new_resonance + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("form"):
                new_form = up[5:]

    new_state = {
        **s,
        "scene": narrative,
        "vitality": new_vitality,
        "resonance": new_resonance,
        "form": new_form,
        "essences": data.get("available_essences", []),
        "available_actions": data.get("available_essences", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_vitality >= 100 and new_resonance >= 100:
        new_state["status"] = "ascended"
        new_state["scene"] += "\n\nTHE BEAST HAS ASCENDED TO GODHOOD. A NEW LEGEND IS BORN."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
