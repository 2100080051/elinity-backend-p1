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

GAME_SLUG = 'elinity-ai-comic-creator'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "High-Fantasy Epic"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Open a new comic universe with theme: {req.theme}. Describe the first panel and initial style."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "A dark city looms under a red moon. Rain slicked streets reflect neon signs.",
            "panel_data": {"number": "1.1", "dialogue": "Narrator: 'It was a cold night in Neo-City...'", "effects": ["Pitter-Patter"], "composition": "Wide Shot"},
            "style_metrics": {"genre": "Noir", "ink_cost": 0},
            "available_panels": ["Walk into the shadows", "Check the flickering sign"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "ink_reserves": 100,
        "current_panel": data.get("panel_data", {}),
        "style": data.get("style_metrics", {}).get("genre", "Modern"),
        "page_number": 1,
        "available_actions": data.get("available_panels", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Writer"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    CURRENT COMIC STATE:
    - Page: {s.get('page_number')} | Last Panel: {s.get('current_panel', {}).get('number')}
    - Ink Reserves: {s.get('ink_reserves')}
    - Art Style: {s.get('style')}
    
    WRITER INPUT: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The ink blots on the page.", "panel_data": s.get("current_panel")}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_ink = s.get("ink_reserves", 100)
    new_page = s.get("page_number", 1)
    new_style = s.get("style", "Modern")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("ink"):
                try: new_ink = max(0, new_ink + int(re.search(r'[-+]?\d+', up).group()))
                except: pass
            elif up.startswith("page+"):
                new_page += 1
            elif up.startswith("style-"):
                new_style = up[6:]

    new_state = {
        **s,
        "scene": narrative,
        "ink_reserves": new_ink,
        "current_panel": data.get("panel_data", s.get("current_panel")),
        "style": new_style,
        "page_number": new_page,
        "available_actions": data.get("available_panels", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_ink <= 0:
        new_state["status"] = "out_of_ink"
        new_state["scene"] += "\n\nTHE INK HAS RUN DRY. THE STORY REMAINS UNFINISHED."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
