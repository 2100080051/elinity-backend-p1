from fastapi import APIRouter, HTTPException, Depends
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
GAME_SLUG = "elinity-the-story-weaver"

class StartReq(BaseModel):
    user_id: str
    genre: Optional[str] = "Fantasy"
    ai_enabled: Optional[bool] = True

class JoinReq(BaseModel):
    session_id: str
    user_id: str

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str # "contribute", "vote"
    content: str # The text contribution or vote choice

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    print(f"DEBUG: Starting game for user_id={req.user_id}")
    
    # NEW: Ensure user exists before doing ANYTHING else
    from utils.guest_manager import ensure_guest_user
    await ensure_guest_user(db, req.user_id)
    
    gm = GameManager(db)
    system_prompt = load_system_prompt(GAME_SLUG)
    
    # Initial Prompt to AI for opening
    opening_json = {}
    if req.ai_enabled:
        prompt = f"Genre: {req.genre}. Generate opening scene JSON."
        try:
            resp = await safe_chat_completion(system_prompt, prompt, max_tokens=400)
            opening_json = json.loads(resp)
        except:
             # Fallback if AI fails or JSON is bad
             opening_json = {"narrative": f"The story begins in a {req.genre} world...", "visual_cue": "Mystery start", "phase": "contribution"}
    else:
        opening_json = {"narrative": f"The story begins in a {req.genre} world...", "phase": "contribution", "visual_cue": "Genre Scene"}

    initial_state = {
        "story_text": [opening_json.get("narrative", "")],
        "genre": req.genre,
        "turn": 1,
        "phase": "contribution",
        "ai_enabled": req.ai_enabled,
        "last_ai_response": opening_json,
        "player_order": [req.user_id],
        "turn_index": 0
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Host", "joined_at": "now"})
    
    # Create Chat Group
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    
    return {
        'ok': True, 
        'session_id': session.session_id, 
        'group_id': group_id,
        'state': session.state
    }

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    current_state = session.state
    
    # Turn Validation
    player_order = current_state.get("player_order", [])
    turn_index = current_state.get("turn_index", 0)
    
    # Robustness: If player order missing, rebuild from players dict
    if not player_order:
         player_order = sorted(list(session.players.keys()))
         
    # Check if it's user's turn
    if player_order and req.user_id != player_order[turn_index % len(player_order)]:
         raise HTTPException(status_code=400, detail="Not your turn!")
    
    # Append user contribution
    new_story_text = current_state.get("story_text", [])
    if req.action == "contribute":
        new_story_text.append(req.content)
    
    # AI Logic
    ai_response = {}
    if current_state.get("ai_enabled"):
        system_prompt = load_system_prompt(GAME_SLUG)
        # Dynamic Feedback Integration
        observer_note = ""
        player_data = session.players.get(req.user_id, {})
        if player_data.get("truth_mismatch"):
             observer_note = f"\n[SHADOW OBSERVER NOTE]: The player is being inconsistent with their persona/profile! {player_data.get('last_commentary')} Adjust your narrative to subtly make fun of this or challenge them on it."

        context = f"Genre: {current_state.get('genre')}\nCurrent Story: {' '.join(new_story_text[-5:])}\nPlayer Input: {req.content}{observer_note}"
        resp_str = await safe_chat_completion(system_prompt, context, max_tokens=400)
        try:
            ai_response = json.loads(resp_str)
        except:
            ai_response = {"narrative": "", "error": "AI JSON Parse Failed", "raw": resp_str}
            
    # Calculate Next Turn
    next_turn_index = (turn_index + 1) % len(player_order)
            
    # Update State
    new_state = {
        "story_text": new_story_text,
        "last_ai_response": ai_response,
        "turn": current_state.get("turn", 0) + 1,
        "phase": ai_response.get("phase", "contribution"),
        "player_order": player_order, # Ensure persisted
        "turn_index": next_turn_index
    }
    
    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "content": req.content})
    return {'ok': True, 'state': updated.state}

@router.post('/join')
async def join(req: JoinReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.join_session(req.session_id, req.user_id, {"role": "Player"})
    
    # Update player order in state
    current_state = dict(session.state or {})
    player_order = list(current_state.get("player_order", []))
    if req.user_id not in player_order:
        player_order.append(req.user_id)
        current_state["player_order"] = player_order
        await gm.update_state(req.session_id, {"player_order": player_order})
    
    # Check for existing group
    from models.chat import Group
    group_name = f"game_{req.session_id}"
    result = await db.execute(select(Group).where(Group.name == group_name))
    group = result.scalars().first()
    if group:
        await add_player_to_game_chat(db, group.id, req.user_id)
        
    return {'ok': True, 'players': session.players, 'group_id': group.id if group else None}
