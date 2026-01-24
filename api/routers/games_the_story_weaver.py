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
    # Ensure user exists
    from utils.guest_manager import ensure_guest_user
    await ensure_guest_user(db, req.user_id)
    
    gm = GameManager(db)
    system_prompt = load_system_prompt(GAME_SLUG)
    
    # 1. AI initialization
    opening_json = {}
    if req.ai_enabled:
        prompt = f"Genre: {req.genre}. The tapestry is blank. Weave the opening thread. Introduce the first world condition. [FORMAT: JSON]"
        try:
            resp = await safe_chat_completion(system_prompt, prompt, max_tokens=600)
            opening_json = json.loads(resp)
        except:
             opening_json = {
                "narrative": f"The story begins in a {req.genre} world under a blood-red moon...", 
                "visual_cue": "Mystery start", 
                "phase": "contribution",
                "fate_paths": ["Investigate the ruins", "Flee into the woods", "Call out into the dark"],
                "atmosphere": "Eerie Mystery"
             }
    else:
        opening_json = {"narrative": f"The story begins in a {req.genre} world...", "phase": "contribution"}

    initial_state = {
        "story_text": [opening_json.get("narrative", "")],
        "history_data": [{"user": "AI", "content": opening_json.get("narrative", ""), "meta": opening_json}],
        "genre": req.genre,
        "turn": 1,
        "chapter": 1,
        "karma": 50,
        "character_arc": "The Nameless Wanderer",
        "world_conditions": ["Blank Slate"],
        "phase": opening_json.get("phase", "contribution"),
        "fate_paths": opening_json.get("fate_paths", []),
        "atmosphere": opening_json.get("atmosphere", "Neutral"),
        "ai_enabled": req.ai_enabled,
        "last_ai_response": opening_json,
        "player_order": [req.user_id],
        "turn_index": 0
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Weaver", "joined_at": "now"})
    
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    
    return {'ok': True, 'session_id': session.session_id, 'group_id': group_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    player_order = s.get("player_order", [])
    turn_index = s.get("turn_index", 0)
    
    if req.user_id not in session.players:
        raise HTTPException(status_code=403, detail="Not in this session!")

    # Context Construction
    history_str = "\n".join(s.get("story_text", [])[-8:])
    
    observer_note = ""
    if session.analysis and req.user_id in session.analysis:
        p_analysis = session.analysis[req.user_id]
        if p_analysis.get("truth_mismatch_detected"):
            observer_note = f"\n[SHADOW OBSERVER: {p_analysis.get('fun_commentary')}]"

    system_prompt = load_system_prompt(GAME_SLUG)
    prompt = f"""
    WORLD STATE:
    - Karma: {s.get('karma')}
    - Arc: {s.get('character_arc')}
    - Conditions: {", ".join(s.get('world_conditions', []))}
    - Atmosphere: {s.get('atmosphere')}
    
    HISTORY:
    {history_str}
    
    PLAYER ACTION:
    Type: {req.action} (selected from previous fate paths if applicable)
    Input: {req.content} {observer_note}
    
    Continue the tale. Return VALID JSON with 'narrative', 'fate_paths', 'atmosphere', and 'visual_cue'.
    Include [METADATA: karma+X, arc=Title, condition=New] if shifts occur.
    """
    
    resp_str = await safe_chat_completion(system_prompt, prompt, max_tokens=800)
    try:
        ai_response = json.loads(resp_str)
    except:
        ai_response = {"narrative": "Fate shifts unexpectedly...", "phase": "contribution", "fate_paths": ["Continue"]}
            
    # Metadata Parsing
    import re
    new_karma = s.get('karma', 50)
    new_arc = s.get('character_arc', "The Nameless Wanderer")
    new_conditions = list(s.get('world_conditions', []))
    
    narrative_text = ai_response.get("narrative", "")
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative_text)
    if meta_match:
        narrative_text = narrative_text.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("karma"):
                try: new_karma = min(100, max(0, new_karma + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("arc="):
                new_arc = up[4:]
            elif up.startswith("condition="):
                new_conditions.append(up[10:])

    # Unique conditions
    new_conditions = list(set(new_conditions))[-3:] # Keep last 3

    story_text = s.get("story_text", [])
    story_text.append(req.content)
    if narrative_text:
        story_text.append(narrative_text)
        
    next_turn_index = (turn_index + 1) % len(player_order) if player_order else 0
            
    new_state = {
        **s,
        "story_text": story_text,
        "history_data": s.get("history_data", []) + [{"user": req.user_id, "action": req.action, "content": req.content, "meta": ai_response}],
        "last_ai_response": {**ai_response, "narrative": narrative_text},
        "karma": new_karma,
        "character_arc": new_arc,
        "world_conditions": new_conditions,
        "atmosphere": ai_response.get("atmosphere", "Neutral"),
        "fate_paths": ai_response.get("fate_paths", []),
        "turn": s.get("turn", 0) + 1,
        "chapter": (s.get("turn", 0) // 5) + 1,
        "phase": ai_response.get("phase", "contribution"),
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
