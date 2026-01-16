from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_db
from sqlalchemy.orm import Session

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
async def start(req: StartReq, db: Session = Depends(get_db)):
    gm = GameManager(db)
    slug = 'elinity-the-long-journey' 
    system = load_system_prompt(slug)
    
    prompt = f'Generate an opening scene for {req.theme} in 2-3 sentences.'
    fallback = 'The game begins.'
    opening_text = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=200, fallback=fallback)
    
    initial_state = {
        "scene": opening_text, 
        "theme": req.theme,
        "turn": 1,
        "status": "active",
        "chat_messages": []
    }
    
    session = gm.create_session(game_slug=slug, host_id=req.user_id, initial_state=initial_state)
    gm.join_session(session.session_id, req.user_id, {"role": "Host", "joined_at": "now"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state, 'players': session.players}

@router.post('/join')
async def join(req: JoinReq, db: Session = Depends(get_db)):
    gm = GameManager(db)
    session = gm.join_session(req.session_id, req.user_id, {"role": req.role})
    return {'ok': True, 'players': session.players, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: Session = Depends(get_db)):
    gm = GameManager(db)
    session = gm.get_session(req.session_id)
    
    slug = 'elinity-the-long-journey'
    system = load_system_prompt(slug)
    
    current_scene = session.state.get("scene", "")
    prompt = f"Current Scene: {current_scene}\nPlayer ({req.user_id}) Action: {req.action}\nNarrate outcome."
    fallback = f"You {req.action}."
    new_scene = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=300, fallback=fallback)
    
    new_state = {
        "scene": new_scene,
        "last_action": req.action,
        "turn": session.state.get("turn", 0) + 1
    }
    
    updated_session = gm.update_state(
        req.session_id, 
        new_state, 
        history_entry={"role": "user", "content": req.action, "user_id": req.user_id, "response": new_scene}
    )
    
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

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
