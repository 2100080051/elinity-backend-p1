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

GAME_SLUG = 'ai-dream-builder'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Midnight Meadow"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Dreamscape with theme: {req.theme}. Begin the first manifestation."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "A thick mist covers your senses. You feel the weight of a world waiting to be born.",
            "dream_data": {"lucidity": 30, "stability": 100, "surrealism": "Low"},
            "available_manifestations": ["Open your eyes", "Reach into the mist"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "lucidity": 30,
        "stability": 100,
        "surrealism": "Low",
        "manifestations": data.get("available_manifestations", []),
        "available_actions": data.get("available_manifestations", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Dreamer"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    DREAM STATE:
    - Lucidity: {s.get('lucidity')}% | Stability: {s.get('stability')}%
    - Surrealism Level: {s.get('surrealism')}
    - Active Manifestations: {", ".join(s.get('manifestations', []))}
    
    DREAMER ACTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The dream flickers. Logic is drifting.", "dream_data": s.get('dream_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_lucidity = s.get("lucidity", 30)
    new_stability = s.get("stability", 100)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("lucidity"):
                try: new_lucidity = min(100, max(0, new_lucidity + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("stability"):
                try: new_stability = min(100, max(0, new_stability + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("surrealism"):
                s["surrealism"] = up[11:]

    new_state = {
        **s,
        "scene": narrative,
        "lucidity": new_lucidity,
        "stability": new_stability,
        "manifestations": data.get("available_manifestations", []),
        "available_actions": data.get("available_manifestations", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_stability <= 0:
        new_state["status"] = "awakened"
        new_state["scene"] += "\n\nTHE DREAM HAS COLLAPSED. YOU HAVE AWAKENED TO REALITY."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
