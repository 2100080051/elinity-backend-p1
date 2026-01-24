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

GAME_SLUG = 'elinity-ai-fortune-teller'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Mystical Forest"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize a prophetic session with the theme: {req.theme}. Reveal the first omen and celestial alignment."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The incense smoke curls into a spiral. The stars whisper your name.",
            "vision_data": {"artifact": "The Fool", "flash": "A child walking toward a cliff of clouds.", "alignment": "New Moon"},
            "available_paths": ["Draw another card", "Ask about the cliff"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "ether": 100,
        "current_vision": data.get("vision_data", {}),
        "alignment": data.get("vision_data", {}).get("alignment", "Unknown"),
        "prophecy_log": [],
        "available_actions": data.get("available_paths", []),
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
    ASTRAL STATE:
    - Alignment: {s.get('alignment')}
    - Ether Level: {s.get('ether')}
    - Last Artifact: {s.get('current_vision', {}).get('artifact')}
    
    SEEKER INQUIRY: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The vision fades into mist.", "vision_data": s.get("current_vision")}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_ether = s.get("ether", 100)
    new_alignment = s.get("alignment", "Unknown")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("ether"):
                try: new_ether = max(0, new_ether + int(re.search(r'[-+]?\d+', up).group()))
                except: pass
            elif up.startswith("alignment+"):
                new_alignment = up[10:]

    new_state = {
        **s,
        "scene": narrative,
        "ether": new_ether,
        "current_vision": data.get("vision_data", s.get("current_vision")),
        "alignment": new_alignment,
        "available_actions": data.get("available_paths", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_ether <= 0:
        new_state["status"] = "faded"
        new_state["scene"] += "\n\nTHE ETHER HAS VANISHED. THE VEIL HAS CLOSED."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
