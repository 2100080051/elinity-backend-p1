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
GAME_SLUG = "elinity-echoes-and-expressions"

class StartReq(BaseModel):
    user_id: str
    ai_enabled: Optional[bool] = True

class JoinReq(BaseModel):
    session_id: str
    user_id: str

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str # "submit_work", "echo_work"
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
        resp = await safe_chat_completion(system_prompt, "Generate creative prompt 1.", max_tokens=300)
        try: initial_ai = json.loads(resp)
        except: initial_ai = {"prompt": "Draw a sound you love.", "visual_theme": "Abstract"}

    initial_state = {
        "current_prompt": initial_ai.get("prompt"),
        "gallery": [], # List of works
        "turn": 1,
        "ai_enabled": req.ai_enabled,
        "last_ai_response": initial_ai
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Host"})
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    return {'ok': True, 'session_id': session.session_id, 'group_id': group_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    current_state = session.state
    
    gallery = current_state.get("gallery", [])
    
    if req.action == "submit_work":
        gallery.append({"user": req.user_id, "work": req.content, "type": "original"})
    elif req.action == "echo_work":
        gallery.append({"user": req.user_id, "work": req.content, "type": "echo", "ref": "previous"})
        
    ai_response = {}
    if current_state.get("ai_enabled"):
        system_prompt = load_system_prompt(GAME_SLUG)
        # Dynamic Feedback Integration
        observer_note = ""
        player_data = session.players.get(req.user_id, {})
        if player_data.get("truth_mismatch"):
             observer_note = f"\n[SHADOW OBSERVER NOTE]: {player_data.get('last_commentary')} Use this in your synthesis to comment on the 'disharmony' or 'mismatch' in the creative expression relative to the player's profile."

        context = f"Prompt: {current_state.get('current_prompt')}\nGallery: {json.dumps(gallery[-3:])}{observer_note}"
        resp_str = await safe_chat_completion(system_prompt, context, max_tokens=400)
        try:
             ai_response = json.loads(resp_str)
        except:
             ai_response = {"echo_synthesis": "A beautiful collection.", "next_challenge": "Create more."}
             
    new_state = {
        "current_prompt": ai_response.get("next_challenge", current_state.get("current_prompt")),
        "gallery": gallery,
        "last_ai_response": ai_response,
        "turn": current_state.get("turn", 0) + 1
    }
    
    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action})
    return {'ok': True, 'state': updated.state}

@router.post('/join')
async def join(req: JoinReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.join_session(req.session_id, req.user_id, {"role": "Player"})
    from models.chat import Group
    group_name = f"game_{req.session_id}"
    result = await db.execute(select(Group).where(Group.name == group_name))
    group = result.scalars().first()
    if group: await add_player_to_game_chat(db, group.id, req.user_id)
    return {'ok': True, 'players': session.players, 'group_id': group.id if group else None}
