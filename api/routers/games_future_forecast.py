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

GAME_SLUG = 'ai-future-forecast'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Neo-Tokyo 2124"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Temporal Simulation with theme: {req.theme}. Offer the first probability node."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "Simulation core initialized. Timelines are diverging. Choose your entry point.",
            "forecast_data": {"probability": 50, "stability": 100, "current_era": "Neo-Tokyo 2124"},
            "available_simulations": ["Scan the district", "Analyze the energy grid"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "probability": 50,
        "stability": 100,
        "era": data.get("forecast_data", {}).get("current_era", "Unknown"),
        "simulations": data.get("available_simulations", []),
        "available_actions": data.get("available_simulations", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Forecaster"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    TEMPORAL STATE:
    - Probability: {s.get('probability')}% | Stability: {s.get('stability')}%
    - Current Era: {s.get('era')}
    
    FORECASTER OVERRIDE: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "Temporal drift detected. Comms link unstable.", "forecast_data": s.get('forecast_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_prob = s.get("probability", 50)
    new_stab = s.get("stability", 100)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("prob"):
                try: new_prob = min(100, max(0, new_prob + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("stability"):
                try: new_stab = min(100, max(0, new_stab + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("era+"):
                s["era"] = up[4:]

    new_state = {
        **s,
        "scene": narrative,
        "probability": new_prob,
        "stability": new_stab,
        "simulations": data.get("available_simulations", []),
        "available_actions": data.get("available_simulations", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_stab <= 0:
        new_state["status"] = "collapsed"
        new_state["scene"] += "\n\nSIMULATION COLLAPSED. THE TIMELINE HAS SHATTERED INTO INFINITE FRAGMENTS."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
