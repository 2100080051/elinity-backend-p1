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

GAME_SLUG = 'elinity-ai-poetry-garden'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Zen Reflection"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Poetry Garden with theme: {req.theme}. Offer the first seed of inspiration."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The soil is rich and silent. A single white petal falls from the sky.",
            "garden_data": {"inspiration": 10, "active_blooms": ["White Lily"], "current_vibe": "Zen Reflection"},
            "available_paths": ["Plant a line", "Observe the lily"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "inspiration": 10,
        "ink": 100,
        "vibe": "Zen Reflection",
        "blooms": data.get("garden_data", {}).get("active_blooms", []),
        "available_actions": data.get("available_paths", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Gardener"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    GARDEN STATE:
    - Inspiration: {s.get('inspiration')}% | Ink: {s.get('ink')}
    - Active Blooms: {", ".join(s.get('blooms', []))}
    - Vibe: {s.get('vibe')}
    
    GARDENER VERSE: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The wind scatters your words like dry leaves.", "garden_data": s.get('garden_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_insp = s.get("inspiration", 10)
    new_ink = s.get("ink", 100)
    new_vibe = s.get("vibe", "Unknown")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("inspiration"):
                try: new_insp = min(100, max(0, new_insp + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("ink"):
                try: new_ink = max(0, new_ink + int(re.search(r'[-+]?\d+', up).group()))
                except: pass
            elif up.startswith("vibe+"):
                new_vibe = up[5:]

    new_state = {
        **s,
        "scene": narrative,
        "inspiration": new_insp,
        "ink": new_ink,
        "vibe": new_vibe,
        "blooms": data.get("garden_data", {}).get("active_blooms", s.get("blooms")),
        "available_actions": data.get("available_paths", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_insp >= 100:
        new_state["status"] = "bloomed"
        new_state["scene"] += "\n\nTHE GARDEN IS IN FULL RESONANCE. A MASTERPIECE HAS GROWN."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
