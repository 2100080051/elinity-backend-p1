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
GAME_SLUG = "elinity-the-long-quest"

class StartReq(BaseModel):
    user_id: str
    campaign_name: Optional[str] = "The Azure Peaks"
    ai_enabled: Optional[bool] = True

class JoinReq(BaseModel):
    session_id: str
    user_id: str
    character_name: Optional[str] = "Traveler"
    character_class: Optional[str] = "Adventurer"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str # "decide", "combat"
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
        resp = await safe_chat_completion(system_prompt, f"Start campaign: {req.campaign_name}", max_tokens=600)
        try: initial_ai = json.loads(resp)
        except: initial_ai = {"narrative": f"You arrive at {req.campaign_name}.", "visual_cue": "Landscape", "quest_log_update": "Arrive safely."}

    initial_state = {
        "campaign_name": req.campaign_name,
        "narrative_log": [initial_ai.get("narrative")],
        "turn": 1,
        "world_state": {},
        "quest_log": [initial_ai.get("quest_log_update")],
        "ai_enabled": req.ai_enabled,
        "last_ai_response": initial_ai
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "GM"})
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    return {'ok': True, 'session_id': session.session_id, 'group_id': group_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    current_state = session.state
    
    quest_log = current_state.get("quest_log", [])
    
    ai_response = {}
    if current_state.get("ai_enabled"):
        system_prompt = load_system_prompt(GAME_SLUG)
        # Dynamic Feedback Integration
        observer_note = ""
        player_data = session.players.get(req.user_id, {})
        if player_data.get("truth_mismatch"):
             observer_note = f"\n[SHADOW OBSERVER NOTE]: {player_data.get('last_commentary')} The player's action here is highly inconsistent with their true profile/persona. Make the AI Game Master comment on this unexpected behavior or introduce a narrative consequence."

        context = f"Campaign: {current_state.get('campaign_name')}\nLast Event: {current_state.get('narrative_log')[-1]}\nAction: {req.content}{observer_note}"
        resp_str = await safe_chat_completion(system_prompt, context, max_tokens=500)
        try:
             ai_response = json.loads(resp_str)
        except:
             ai_response = {"narrative": "You move on.", "options": ["Continue"]}
             
    if ai_response.get("quest_log_update"):
        quest_log.append(ai_response["quest_log_update"])
        
    new_narrative = current_state.get("narrative_log", [])
    new_narrative.append(ai_response.get("narrative", ""))
        
    new_state = {
        "quest_log": quest_log,
        "narrative_log": new_narrative,
        "last_ai_response": ai_response,
        "turn": current_state.get("turn", 0) + 1
    }
    
    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "content": req.content})
    return {'ok': True, 'state': updated.state}

@router.post('/join')
async def join(req: JoinReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.join_session(req.session_id, req.user_id, {"role": "Player", "character": req.character_name, "class": req.character_class})
    from models.chat import Group
    group_name = f"game_{req.session_id}"
    result = await db.execute(select(Group).where(Group.name == group_name))
    group = result.scalars().first()
    if group: await add_player_to_game_chat(db, group.id, req.user_id)
    return {'ok': True, 'players': session.players, 'group_id': group.id if group else None}
