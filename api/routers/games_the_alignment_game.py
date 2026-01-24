from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_db, get_async_db
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import json

router = APIRouter()

class StartReq(BaseModel):
    user_id: Optional[str] = "anon"
    theme: Optional[str] = "DEFAULT"

class JoinReq(BaseModel):
    session_id: str
    user_id: str
    role: Optional[str] = "Player"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

class ChatReq(BaseModel):
    session_id: str
    user_id: str
    message: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    # Ensure user exists
    from utils.guest_manager import ensure_guest_user
    await ensure_guest_user(db, req.user_id)
    
    gm = GameManager(db)
    slug = 'elinity-the-alignment-game' 
    system = load_system_prompt(slug)
    
    prompt = f'Initialize the moral diagnostic for theme: {req.theme}. Present the first aperture. [FORMAT: JSON]'
    try:
        resp = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=600)
        initial_ai = json.loads(resp)
    except:
        initial_ai = {
            "scenario": "You stand before a cosmic scale. A digital soul is crying for deletion.",
            "verdict": "The diagnostic begins.",
            "archetype": "The Unawakened",
            "options": [
                {"label": "Delete it", "description": "Uphold efficiency."},
                {"label": "Save it", "description": "Embrace empathy."}
            ]
        }

    initial_state = {
        "scenario": initial_ai.get("scenario"),
        "verdict": initial_ai.get("verdict"),
        "archetype": initial_ai.get("archetype"),
        "options": initial_ai.get("options", []),
        "theme": req.theme,
        "order": 50,
        "light": 50,
        "dissonance": 0,
        "vessel_integrity": 100,
        "turn": 1,
        "last_ai_response": initial_ai,
        "history": []
    }
    
    session = await gm.create_session(game_slug=slug, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Seeker"})
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    slug = 'elinity-the-alignment-game'
    system = load_system_prompt(slug)
    
    # Observer logic
    observer_note = ""
    if session.analysis and req.user_id in session.analysis:
        p_analysis = session.analysis[req.user_id]
        if p_analysis.get("truth_mismatch_detected"):
            observer_note = f"\n[SHADOW OBSERVER: {p_analysis.get('fun_commentary')}]"

    context = f"""
    IDENTITY GEOMETRY:
    - Order/Chaos: {s.get('order')}
    - Light/Dark: {s.get('light')}
    - Vessel Integrity: {s.get('vessel_integrity')}
    - Prev Archetype: {s.get('archetype')}
    
    LAST APERTURE: {s.get('scenario')}
    PLAYER RESOLUTION: {req.action}
    {observer_note}
    
    Process the resolution. Compute the next aperture.
    Include [METADATA: order+X, light+X, dissonance=X] in 'scenario'.
    Return VALID JSON.
    """
    
    resp_str = await safe_chat_completion(system or '', context, max_tokens=800)
    try:
        ai_response = json.loads(resp_str)
    except:
        ai_response = {"scenario": "Reality ripples.", "verdict": "Indecision is also a choice.", "options": [{"label": "Continue", "description": "Proceed"}]}
             
    # Parse Metadata
    import re
    new_order = s.get('order', 50)
    new_light = s.get('light', 50)
    new_diss = s.get('dissonance', 0)
    
    scenario_text = ai_response.get("scenario", "")
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', scenario_text)
    if meta_match:
        scenario_text = scenario_text.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("order"):
                try: new_order = min(100, max(0, new_order + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("light"):
                try: new_light = min(100, max(0, new_light + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("dissonance"):
                try: new_diss = int(re.search(r'\d+', up).group())
                except: pass

    # Integrity check: High dissonance damages the vessel
    new_integrity = s.get('vessel_integrity', 100)
    if new_diss > 70: new_integrity -= 10

    new_state = {
        **s,
        "order": new_order,
        "light": new_light,
        "dissonance": new_diss,
        "vessel_integrity": new_integrity,
        "scenario": scenario_text,
        "verdict": ai_response.get("verdict"),
        "archetype": ai_response.get("archetype", s.get("archetype")),
        "options": ai_response.get("options", []),
        "visual_geometry": ai_response.get("visual_geometry"),
        "last_ai_response": {**ai_response, "scenario": scenario_text},
        "turn": s.get("turn", 0) + 1,
        "history": (s.get("history", []) + [{"scenario": s.get("scenario"), "choice": req.action}])[-10:]
    }
    
    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action})
    return {'ok': True, 'state': updated.state}

@router.post('/chat')
async def chat(req: ChatReq, db: Session = Depends(get_db)):
    gm = GameManager(db)
    session = gm.get_session(req.session_id)
    
    messages = list(session.state.get("chat_messages", []))
    new_msg = {
        "user_id": req.user_id,
        "message": req.message,
        "timestamp": "now"
    }
    messages.append(new_msg)
    
    if len(messages) > 50: messages = messages[-50:]
    
    updated_session = gm.update_state(req.session_id, {"chat_messages": messages})
    return {'ok': True, 'chat_messages': updated_session.state.get("chat_messages")}

@router.get('/status/{session_id}')
async def status(session_id: str, db: Session = Depends(get_db)):
    gm = GameManager(db)
    session = gm.get_session(session_id)
    return {'ok': True, 'state': session.state, 'players': session.players, 'history': session.history}
