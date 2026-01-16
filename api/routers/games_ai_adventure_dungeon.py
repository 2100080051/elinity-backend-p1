from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class StartReq(BaseModel):
    user_id: Optional[str] = "anon"
    theme: Optional[str] = "FANTASY_RUINS"

class JoinReq(BaseModel):
    session_id: str
    user_id: str
    role: Optional[str] = "Adventurer"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    """Initialize a new persistent game session."""
    gm = GameManager(db)
    slug = 'ai-adventure-dungeon'
    system = load_system_prompt(slug)
    
    # 1. AI initialization
    prompt = f'Generate an opening dungeon scene for theme {req.theme} in 2-3 sentences.'
    fallback = 'You enter a dimly-lit cavern; the air smells of damp stone.'
    opening_text = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=200, fallback=fallback)
    
    # 2. Create DB Session
    initial_state = {
        "scene": opening_text, 
        "narrative": opening_text, # Standardize
        "theme": req.theme,
        "turn": 1,
        "status": "waiting_for_players" 
    }
    
    # Auto-add host as player - Fix: use await
    session = await gm.create_session(game_slug=slug, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Host", "joined_at": "now"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state, 'players': session.players}

@router.post('/join')
async def join(req: JoinReq, db: AsyncSession = Depends(get_async_db)):
    """Join an existing session."""
    gm = GameManager(db)
    session = await gm.join_session(req.session_id, req.user_id, {"role": req.role})
    return {'ok': True, 'players': session.players}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    """Submit a move."""
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    
    # 1. AI Processing
    slug = 'ai-adventure-dungeon'
    system = load_system_prompt(slug)
    
    # Context Construction
    history = session.history or []
    current_scene = session.state.get("scene", "")
    
    prompt = f"Current Scene: {current_scene}\nPlayer ({req.user_id}) Action: {req.action}\nNarrate the outcome and describe the next room/challenge."
    
    fallback = f"You move forward. {req.action} happens."
    new_scene = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=300, fallback=fallback)
    
    # 2. Update State
    new_state = {
        "scene": new_scene,
        "narrative": new_scene, # Standardize
        "last_action": req.action,
        "last_actor": req.user_id,
        "turn": session.state.get("turn", 0) + 1
    }
    
    # 3. Persist
    updated_session = await gm.update_state(
        req.session_id, 
        new_state, 
        history_entry={"user": req.user_id, "action": "action", "content": req.action, "result": new_scene}
    )
    
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    """Poll for latest state."""
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    return {'ok': True, 'state': session.state, 'players': session.players, 'history': session.history}
