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

GAME_SLUG = 'ai-heist'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Shadow Bank"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Heist with theme: {req.theme}. Provide the first objective and tactical scan."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The blueprints are on the table. The sensors are cold. For now.",
            "heist_data": {"heat": 0, "vault_integrity": 100, "current_objective": "Breach the outer perimeter"},
            "available_tactics": ["Climb the ventilation shaft", "Bypass the main gate"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "heat": 0,
        "integrity": 100,
        "loot": 0,
        "objective": data.get("heist_data", {}).get("current_objective", "Unknown"),
        "available_actions": data.get("available_tactics", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Infiltrator"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    HEIST STATUS:
    - Heat Level: {s.get('heat')}% | Vault Integrity: {s.get('integrity')}%
    - Current Objective: {s.get('objective')}
    - Secured Loot: ${s.get('loot')}
    
    INFILTRATOR ACTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "Comms static. The team is waiting for orders.", "heist_data": s.get('heist_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_heat = s.get("heat", 0)
    new_integrity = s.get("integrity", 100)
    new_loot = s.get("loot", 0)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("heat"):
                try: new_heat = min(100, max(0, new_heat + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("vault"):
                try: new_integrity = min(100, max(0, new_integrity + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("loot"):
                try: new_loot += int(re.search(r'[-+]?\d+', up).group())
                except: pass

    new_state = {
        **s,
        "scene": narrative,
        "heat": new_heat,
        "integrity": new_integrity,
        "loot": new_loot,
        "objective": data.get("heist_data", {}).get("current_objective", s.get("objective")),
        "available_actions": data.get("available_tactics", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_heat >= 100:
        new_state["status"] = "busted"
        new_state["scene"] += "\n\nHEAT LEVEL CRITICAL. LAW ENFORCEMENT HAS SURROUNDED THE PREMISES. ABORT!"
    elif new_integrity <= 0:
        new_state["status"] = "breached"
        new_state["scene"] += "\n\nVAULT BREACHED. SECURE THE LOOT AND HEAD TO THE EXTRACTION POINT!"

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
