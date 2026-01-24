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

GAME_SLUG = 'ai-symbol-quest'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Void Cathedral"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Sacred Lexicon with theme: {req.theme}. Present the first cosmic glyph."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "A single glyph burns white against the darkness. It waits for a seeker.",
            "symbol_data": {"glyph_resonance": 10, "alignment": "The Seeker", "active_symbol": "Unknown"},
            "available_runes": ["Study the glyph", "Touch the light"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "resonance": 10,
        "alignment": "The Seeker",
        "symbol": data.get("symbol_data", {}).get("active_symbol", "Unknown"),
        "runes": data.get("available_runes", []),
        "available_actions": data.get("available_runes", []),
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
    LEXICON STATE:
    - Glyph Resonance: {s.get('resonance')}% | Archetype: {s.get('alignment')}
    - Active Symbol: {s.get('symbol')}
    
    SEEKER INSCRIPTION: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The ink of fate is dry. The spirits remain silent.", "symbol_data": s.get('symbol_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_resonance = s.get("resonance", 10)
    new_alignment = s.get("alignment", "The Seeker")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("resonance"):
                try: new_resonance = min(100, max(0, new_resonance + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("alignment"):
                new_alignment = up[10:]

    new_state = {
        **s,
        "scene": narrative,
        "resonance": new_resonance,
        "alignment": new_alignment,
        "symbol": data.get("symbol_data", {}).get("active_symbol", s.get("symbol")),
        "runes": data.get("available_runes", []),
        "available_actions": data.get("available_runes", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_resonance >= 100:
        new_state["status"] = "enlightened"
        new_state["scene"] += "\n\nTHE TRUTH IS REVEALED. YOU HAVE BECOME THE INSCRIBER."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
