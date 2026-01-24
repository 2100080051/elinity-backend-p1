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

GAME_SLUG = 'elinity-ai-improv-theater'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Gothic Horror"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Raise the curtain on a new scene with theme: {req.theme}. Introduce the first prompt and set the stage energy."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "[The stage is dark. A single spotlight hits a wooden chair.]\nENACTOR: 'The audience is waiting. What's our first move?'",
            "theater_data": {"energy": 50, "applause_level": "Silent", "active_props": ["Wooden Chair"], "current_mask": "Neutral"},
            "available_cues": ["Sit on the chair", "Look at the wings"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "energy": 50,
        "applause": 0,
        "mask": "Neutral",
        "props": data.get("theater_data", {}).get("active_props", []),
        "available_actions": data.get("available_cues", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Performer"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    STAGE STATE:
    - Scene Energy: {s.get('energy')}% | Applause: {s.get('applause')}%
    - Active Props: {", ".join(s.get('props', []))}
    - Current Mask: {s.get('mask')}
    
    PERFORMER ACTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "[The Enactor looks confused.]\nENACTOR: 'I didn't quite catch that cue!'", "theater_data": {"energy": s.get('energy'), "applause_level": "Awkward Silence"}}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_energy = s.get("energy", 50)
    new_applause = s.get("applause", 0)
    new_mask = s.get("mask", "Neutral")
    new_props = list(s.get("props", []))
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("energy"):
                try: new_energy = min(100, max(0, new_energy + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("applause"):
                try: new_applause = min(100, max(0, new_applause + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("mask+"):
                new_mask = up[5:]
            elif up.startswith("prop+"):
                new_props.append(up[5:])

    new_state = {
        **s,
        "scene": narrative,
        "energy": new_energy,
        "applause": new_applause,
        "mask": new_mask,
        "props": new_props,
        "available_actions": data.get("available_cues", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_energy <= 0:
        new_state["status"] = "curtains"
        new_state["scene"] += "\n\n[The energy has flatlined. The curtains fall prematurely.]\nENACTOR: 'That's show business, baby.'"

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
