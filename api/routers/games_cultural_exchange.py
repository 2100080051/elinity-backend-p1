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

GAME_SLUG = 'ai-cultural-exchange'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Solaris Confederation"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Cultural Exchange with theme: {req.theme}. Introduce the first delegation."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "A shimmering gateway opens. A delegation awaits your greeting.",
            "exchange_data": {"trust_level": 30, "insight_score": 0, "active_artifact": "Unknown"},
            "available_gestures": ["Bow deeply", "Offer a greeting"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "trust": 30,
        "insight": 0,
        "artifact": data.get("exchange_data", {}).get("active_artifact", "Unknown"),
        "gestures": data.get("available_gestures", []),
        "available_actions": data.get("available_gestures", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Mediator"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    EXCHANGE STATE:
    - Diplomatic Trust: {s.get('trust')}% | Insight Score: {s.get('insight')}
    - Current Artifact: {s.get('artifact')}
    
    DIPLOMATIC GESTURE: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "A misunderstanding has occurred. Tension rises.", "exchange_data": s.get('exchange_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_trust = s.get("trust", 30)
    new_insight = s.get("insight", 0)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("trust"):
                try: new_trust = min(100, max(0, new_trust + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("insight"):
                try: new_insight = max(0, new_insight + int(re.search(r'[-+]?\d+', up).group()))
                except: pass

    new_state = {
        **s,
        "scene": narrative,
        "trust": new_trust,
        "insight": new_insight,
        "artifact": data.get("exchange_data", {}).get("active_artifact", s.get("artifact")),
        "gestures": data.get("available_gestures", []),
        "available_actions": data.get("available_gestures", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_trust >= 100:
        new_state["status"] = "unified"
        new_state["scene"] += "\n\nTOTAL UNITY ACHIEVED. THE BRIDGE OF UNDERSTANDING IS PERMANENT."
    elif new_trust <= 0:
        new_state["status"] = "collapsed"
        new_state["scene"] += "\n\nNEGOTIATIONS HAVE COLLAPSED. THE EXCHANGE HAS ENDED IN DISCORD."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
