from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.game_chat import create_game_chat_group, add_player_to_game_chat

router = APIRouter()
GAME_SLUG = "elinity-myth-maker-arena"

class StartReq(BaseModel):
    user_id: str
    archetype: Optional[str] = "Warrior"
    ai_enabled: Optional[bool] = True

class JoinReq(BaseModel):
    session_id: str
    user_id: str
    archetype: Optional[str] = "Seer"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str # "contribute"
    content: str 

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    # Ensure guest user exists before any DB operations
    from utils.guest_manager import ensure_guest_user
    await ensure_guest_user(db, req.user_id)
    
    gm = GameManager(db)
    system_prompt = load_system_prompt(GAME_SLUG)
    
    initial_ai = {}
    if req.ai_enabled:
        resp = await safe_chat_completion(system_prompt, f"Start myth for Archetype: {req.archetype}. Stage: Origin.", max_tokens=300)
        try: initial_ai = json.loads(resp)
        except: initial_ai = {"narrative": f"The {req.archetype} was born...", "next_stage": "Conflict"}

    initial_state = {
        "stage": "Origin",
        "turn": 1,
        "myth_log": [initial_ai],
        "ai_enabled": req.ai_enabled,
        "last_ai_response": initial_ai
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Host", "archetype": req.archetype})
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    return {'ok': True, 'session_id': session.session_id, 'group_id': group_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    current_state = session.state
    
    myth_log = current_state.get("myth_log", [])
    current_stage = current_state.get("stage")
    
    ai_response = {}
    if current_state.get("ai_enabled"):
        system_prompt = load_system_prompt(GAME_SLUG)
        
        # INJECT OBSERVER FEEDBACK
        observer_context = ""
        if session.analysis and req.user_id in session.analysis:
            p_analysis = session.analysis[req.user_id]
            if p_analysis.get("truth_mismatch_detected"):
                observer_context = f"\n[SHADOW OBSERVER NOTE: Player is being inconsistent with their profile! {p_analysis.get('fun_commentary')}. Adjustment: {p_analysis.get('strategy_adjustment_suggestion')}]"

        context = f"Stage: {current_stage}\nMyth So Far: {json.dumps(myth_log[-2:])}\nPlayer Action: {req.content}{observer_context}"
        resp_str = await safe_chat_completion(system_prompt, context, max_tokens=450)
        try:
             ai_response = json.loads(resp_str)
        except:
             ai_response = {"narrative": "The myth grows.", "next_stage": "Unknown"}
    
    if ai_response:
        myth_log.append(ai_response)
        
    new_state = {
        "stage": ai_response.get("next_stage", current_stage),
        "myth_log": myth_log,
        "last_ai_response": ai_response,
        "turn": current_state.get("turn", 0) + 1
    }
    
    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": "action", "content": req.content})
    return {'ok': True, 'state': updated.state}

@router.post('/join')
async def join(req: JoinReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.join_session(req.session_id, req.user_id, {"role": "Player", "archetype": req.archetype})
    from models.chat import Group
    group_name = f"game_{req.session_id}"
    result = await db.execute(select(Group).where(Group.name == group_name))
    group = result.scalars().first()
    if group: await add_player_to_game_chat(db, group.id, req.user_id)
    return {'ok': True, 'players': session.players, 'group_id': group.id if group else None}
