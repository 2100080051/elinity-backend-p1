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

GAME_SLUG = 'ai-micro-mysteries'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Shattered Genome"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Micro-Investigation with theme: {req.theme}. Offer the first magnification level."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "Slide prepared. The world shrinks. Investigation initialized.",
            "micro_data": {"magnification": "Cellular", "clarity": 10, "current_anomaly": "None"},
            "available_tools": ["Calibrate lens", "Scan the sample"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "magnification": "Cellular",
        "clarity": 10,
        "anomaly": data.get("micro_data", {}).get("current_anomaly", "None"),
        "tools": data.get("available_tools", []),
        "available_actions": data.get("available_tools", []),
        "status": "active",
        "stability": 100,
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Investigator"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    MICRO STATE:
    - Magnification: {s.get('magnification')} | Clarity: {s.get('clarity')}%
    - Current Anomaly: {s.get('anomaly')} | Stability: {s.get('stability')}%
    
    INVESTIGATOR COMMAND: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "Quantum interference detected. Sample integrity compromised.", "micro_data": s.get('micro_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_clarity = s.get("clarity", 10)
    new_stability = s.get("stability", 100)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("magnification"):
                s["magnification"] = up[14:]
            elif up.startswith("clarity"):
                try: new_clarity = min(100, max(0, new_clarity + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("stability"):
                try: new_stability = min(100, max(0, new_stability + int(re.search(r'[-+]?\d+', up).group())))
                except: pass

    new_state = {
        **s,
        "scene": narrative,
        "clarity": new_clarity,
        "stability": new_stability,
        "anomaly": data.get("micro_data", {}).get("current_anomaly", s.get("anomaly")),
        "tools": data.get("available_tools", []),
        "available_actions": data.get("available_tools", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_clarity >= 100:
        new_state["status"] = "solved"
        new_state["scene"] += "\n\nMYSTERY SOLVED. THE QUANTUM TRUTH HAS BEEN EXPOSED."
    elif new_stability <= 0:
        new_state["status"] = "collapsed"
        new_state["scene"] += "\n\nSAMPLE COLLAPSED. THE QUANTUM WAVEFORM HAS SHATTERED."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
