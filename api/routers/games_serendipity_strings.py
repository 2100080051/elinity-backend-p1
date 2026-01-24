from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import re
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.game_chat import create_game_chat_group, add_player_to_game_chat

router = APIRouter()
GAME_SLUG = "elinity-serendipity-strings"

class StartReq(BaseModel):
    user_id: str
    ai_enabled: Optional[bool] = True

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str # "answer", "weave"
    content: str 

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    from utils.guest_manager import ensure_guest_user
    await ensure_guest_user(db, req.user_id)
    
    gm = GameManager(db)
    system_prompt = load_system_prompt(GAME_SLUG)
    
    initial_ai = {}
    if req.ai_enabled:
        resp = await safe_chat_completion(system_prompt, "Initialize the Temporal Web. Present the first thread.", max_tokens=600)
        try: initial_ai = json.loads(resp)
        except: initial_ai = {"prompt": "What is a coincidence that changed your life?", "serendipity_insight": "The web is thin. We must weave."}

    initial_state = {
        "prompt": initial_ai.get("prompt"),
        "insight": initial_ai.get("serendipity_insight"),
        "depth": 10,
        "resonance": 50,
        "thread": initial_ai.get("web_data", {}).get("active_thread", "The Awakening"),
        "responses": {},
        "connections": [],
        "turn": 1,
        "status": "active",
        "last_ai_response": initial_ai
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Weaver"})
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    return {'ok': True, 'session_id': session.session_id, 'group_id': group_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    responses = dict(s.get("responses", {}))
    
    if req.action == "answer":
        responses[req.user_id] = req.content
        new_state = {**s, "responses": responses}
        updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "answer": req.content})
        return {'ok': True, 'state': updated.state}

    # Weave Logic (AI Analysis)
    system_prompt = load_system_prompt(GAME_SLUG)
    observer_note = ""
    if session.analysis and req.user_id in session.analysis:
        p_analysis = session.analysis[req.user_id]
        if p_analysis.get("truth_mismatch_detected"):
            observer_note = f"\n[SHADOW OBSERVER: {p_analysis.get('fun_commentary')}]"

    context = f"""
    THE WEB:
    - Current Thread: {s.get('thread')}
    - Depth: {s.get('depth')}% | Resonance: {s.get('resonance')}%
    
    GROUP RESPONSES: {json.dumps(responses)} {observer_note}
    
    Analyze the fabric of these lives. Identify the shared strings. Prepare the next pull.
    Include [METADATA: depth+X, resonance+X, thread=Name] in 'serendipity_insight'.
    Return VALID JSON.
    """
    
    resp_str = await safe_chat_completion(system_prompt, context, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"prompt": "What else remains hidden?", "serendipity_insight": "The web trembles with untold stories."}

    # Metadata Parsing
    insight = data.get("serendipity_insight", "")
    new_depth = s.get("depth", 10)
    new_resonance = s.get("resonance", 50)
    new_thread = s.get("thread", "The Awakening")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', insight)
    if meta_match:
        insight = insight.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("depth"):
                try: new_depth = min(100, max(0, new_depth + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("resonance"):
                try: new_resonance = min(100, max(0, new_resonance + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("thread="):
                new_thread = up[7:]

    current_connections = list(s.get("connections", []))
    if data.get("connections"):
        current_connections.extend(data["connections"])

    new_state = {
        **s,
        "prompt": data.get("prompt"),
        "insight": insight,
        "depth": new_depth,
        "resonance": new_resonance,
        "thread": new_thread,
        "connections": current_connections[-20:],
        "responses": {}, # Clear for next round
        "turn": s.get("turn", 0) + 1
    }
    
    if new_depth >= 100:
        new_state["status"] = "woven"
        new_state["insight"] += "\n\nTHE WEB IS COMPLETE. YOU ARE BOUND BY STRINGS OF LIGHT."

    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": "weave"})
    return {'ok': True, 'state': updated.state}

@router.post('/join')
async def join(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.join_session(req.session_id, req.user_id, {"role": "Seeker"})
    from models.chat import Group
    group_name = f"game_{req.session_id}"
    result = await db.execute(select(Group).where(Group.name == group_name))
    group = result.scalars().first()
    if group: await add_player_to_game_chat(db, group.id, req.user_id)
    return {'ok': True, 'players': session.players, 'group_id': group.id if group else None}
