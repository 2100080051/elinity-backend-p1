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

GAME_SLUG = 'elinity-meme-forge'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Algorithm"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Meme Forge with theme: {req.theme}. Offer the first trending template."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The Algorithm is hungry. Which template will you sacrifice?",
            "meme_data": {"virality_percent": 10, "current_format": "Distracted AI", "internet_reaction": "Waiting..."},
            "available_templates": ["Two Buttons", "This is Fine"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "virality": 10,
        "dankness": 0,
        "format": data.get("meme_data", {}).get("current_format", "Unknown"),
        "templates": data.get("available_templates", []),
        "available_actions": data.get("available_templates", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Creator"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    ALGORITHM STATUS:
    - Virality: {s.get('virality')}% | Dankness: {s.get('dankness')}
    - Current Format: {s.get('format')}
    - Templates Seen: {", ".join(s.get('templates', []))}
    
    CREATOR INPUT: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The meme flopped. 0 upvotes.", "meme_data": s.get('meme_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_viral = s.get("virality", 10)
    new_dank = s.get("dankness", 0)
    new_format = data.get("meme_data", {}).get("current_format", s.get("format"))
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("virality"):
                try: new_viral = min(100, max(0, new_viral + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("dankness"):
                try: new_dank = max(0, new_dank + int(re.search(r'[-+]?\d+', up).group()))
                except: pass

    new_state = {
        **s,
        "scene": narrative,
        "virality": new_viral,
        "dankness": new_dank,
        "format": new_format,
        "available_actions": data.get("available_templates", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_viral >= 100:
        new_state["status"] = "viral"
        new_state["scene"] += "\n\nCRITICAL MASS ACHIEVED. THE INTERNET IS YOURS."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
