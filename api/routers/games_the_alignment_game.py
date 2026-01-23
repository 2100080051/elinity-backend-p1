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
    
    prompt = f'Generate a complex moral dilemma for the theme: {req.theme}. Include a scenario and a question. [FORMAT: JSON]'
    fallback = '{"scenario": "A thief is caught.", "analysis": "Do you punish them?"}'
    resp = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=400, fallback=fallback)
    
    initial_ai = {}
    try: initial_ai = json.loads(resp)
    except: initial_ai = json.loads(fallback)

    initial_state = {
        "scenario": initial_ai.get("scenario"),
        "analysis": initial_ai.get("analysis"),
        "theme": req.theme,
        "law": 50,
        "good": 50,
        "turn": 1,
        "last_ai_response": initial_ai
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
    Current Alignment: Law={s.get('law')}, Good={s.get('good')}
    Scenario: {s.get('scenario')}
    Player Judgment: {req.action}
    {observer_note}
    
    Narrate the consequences and provide a new dilemma.
    Include [UPDATE: law+X, good+X] tags in the 'scenario' field.
    Respond in JSON.
    """
    
    resp_str = await safe_chat_completion(system or '', context, max_tokens=600)
    try:
        ai_response = json.loads(resp_str)
    except:
        ai_response = {"scenario": "A new day dawns.", "analysis": "What now?"}
             
    # Parse Updates
    import re
    new_law = s.get('law', 50)
    new_good = s.get('good', 50)
    
    narrative_text = ai_response.get("scenario", "")
    meta_match = re.search(r'\[UPDATE:\s*(.*?)\]', narrative_text)
    if meta_match:
        narrative_text = narrative_text.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("law"):
                new_law = min(100, max(0, new_law + int(up[3:])))
            elif up.startswith("good"):
                new_good = min(100, max(0, new_good + int(up[4:])))

    new_state = {
        **s,
        "law": new_law,
        "good": new_good,
        "scenario": narrative_text,
        "analysis": ai_response.get("analysis"),
        "last_ai_response": {**ai_response, "scenario": narrative_text},
        "turn": s.get("turn", 0) + 1
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
