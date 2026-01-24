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

GAME_SLUG = 'elinity-ai-roast-tost'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Digital Presence"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Open the Singe-Master's Roast Arena with theme: {req.theme}. Deliver the opening burn."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "Welcome to the grill. You look like you're ready for a medium-rare ego check.",
            "burn_report": {"intensity": 5, "damage": "Surface Level", "audience_reaction": "Snickering"},
            "available_reactions": ["Let's go", "Easy now"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "char_level": 50,
        "tension": 10,
        "vibe": "Snickering",
        "last_burn": data.get("burn_report", {}),
        "available_actions": data.get("available_reactions", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Target"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    THE GRILL:
    - Char Points: {s.get('char_level')} | Tension: {s.get('tension')}%
    - Current Vibe: {s.get('vibe')}
    - Last Intensity: {s.get('last_burn', {}).get('intensity')}
    
    TARGET RESPONSE: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The crowd stares in silence. Awkward.", "burn_report": s.get('last_burn')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_char = s.get("char_level", 50)
    new_tension = s.get("tension", 10)
    new_vibe = s.get("vibe", "Mixed")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("char"):
                try: new_char = max(0, new_char + int(re.search(r'[-+]?\d+', up).group()))
                except: pass
            elif up.startswith("tension"):
                try: new_tension = min(100, max(0, new_tension + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("vibe-"):
                new_vibe = up[5:]

    new_state = {
        **s,
        "scene": narrative,
        "char_level": new_char,
        "tension": new_tension,
        "vibe": new_vibe,
        "last_burn": data.get("burn_report", s.get("last_burn")),
        "available_actions": data.get("available_reactions", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_tension >= 100:
        new_state["status"] = "meltdown"
        new_state["scene"] += "\n\nTENSION COLLAPSE. THE GRILL HAS OVERHEATED."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
