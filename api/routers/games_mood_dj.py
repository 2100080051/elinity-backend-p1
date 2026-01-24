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

GAME_SLUG = 'ai-mood-dj'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Night City"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Soundscape with theme: {req.theme}. Start the first track."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "Static fades out. A low hum fills the air. The Frequency is offline but listening.",
            "dj_data": {"vibe_level": 20, "bpm": 80, "current_genre": "Void Ambient"},
            "available_tracks": ["Power up the console", "Scan for frequencies"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "vibe": 20,
        "bpm": 80,
        "genre": data.get("dj_data", {}).get("current_genre", "Unknown"),
        "tracks": data.get("available_tracks", []),
        "available_actions": data.get("available_tracks", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Vibe-Master"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    SOUNDSCAPE STATE:
    - Vibe Level: {s.get('vibe')}% | BPM: {s.get('bpm')}
    - Current Genre: {s.get('genre')}
    
    MIXER INPUT: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The signal is lost in the noise.", "dj_data": s.get('dj_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_vibe = s.get("vibe", 20)
    new_bpm = s.get("bpm", 80)
    new_genre = s.get("genre", "Unknown")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("vibe"):
                try: new_vibe = min(100, max(0, new_vibe + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("bpm"):
                try: new_bpm = min(200, max(40, new_bpm + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("genre+"):
                new_genre = up[6:]

    new_state = {
        **s,
        "scene": narrative,
        "vibe": new_vibe,
        "bpm": new_bpm,
        "genre": new_genre,
        "tracks": data.get("available_tracks", []),
        "available_actions": data.get("available_tracks", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_vibe >= 100:
        new_state["status"] = "ascended"
        new_state["scene"] += "\n\nTHE VIBE HAS REACHED SINGULARITY. YOU ARE THE FREQUENCY."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
