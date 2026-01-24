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

GAME_SLUG = 'ai-artifact-maker'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Ethereal Porcelain"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Vault with theme: {req.theme}. Present the first material choice."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "A block of raw potential sits on the pedestal. The Curator waits.",
            "artifact_data": {"material_integrity": 100, "historical_value": 0, "current_stage": "Raw Material"},
            "available_actions": ["Choose the chisel", "Scan the grain"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "integrity": 100,
        "value": 0,
        "stage": data.get("artifact_data", {}).get("current_stage", "Unknown"),
        "actions": data.get("available_actions", []),
        "available_actions": data.get("available_actions", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Craftsman"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    VAULT STATE:
    - Material Integrity: {s.get('integrity')}% | Historical Value: {s.get('value')}
    - Current Stage: {s.get('stage')}
    
    CRAFTSMAN ACTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The tool slips. The material cracks.", "artifact_data": s.get('artifact_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_integrity = s.get("integrity", 100)
    new_value = s.get("value", 0)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("integrity"):
                try: new_integrity = min(100, max(0, new_integrity + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("value"):
                try: new_value = max(0, new_value + int(re.search(r'[-+]?\d+', up).group()))
                except: pass
            elif up.startswith("stage"):
                s["stage"] = up[6:]

    new_state = {
        **s,
        "scene": narrative,
        "integrity": new_integrity,
        "value": new_value,
        "actions": data.get("available_actions", []),
        "available_actions": data.get("available_actions", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_integrity <= 0:
        new_state["status"] = "destroyed"
        new_state["scene"] += "\n\nTHE ARTIFACT HAS SHATTERED. THE LEGACY IS LOST."
    elif s.get("turn", 0) >= 10:
        new_state["status"] = "archived"
        new_state["scene"] += "\n\nTHE ARTIFACT IS COMPLETE. IT HAS BEEN PLACED IN THE ETERNAL COLLECTION."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
