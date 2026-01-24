from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
import json
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.game_chat import create_game_chat_group, add_player_to_game_chat

router = APIRouter()
GAME_SLUG = "elinity-memory-mosaic"

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Childhood Adventures"
    ai_enabled: Optional[bool] = True

class JoinReq(BaseModel):
    session_id: str
    user_id: str

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str # "share_memory", "generate_mosaic"
    content: str 

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    # Ensure user exists
    from utils.guest_manager import ensure_guest_user
    await ensure_guest_user(db, req.user_id)
    
    gm = GameManager(db)
    slug = 'elinity-memory-mosaic'
    system = load_system_prompt(slug)
    
    prompt = f"Initialize the Lens of Atavism for theme: {req.theme}. Capture the first frequency. [FORMAT: JSON]"
    try:
        resp = await safe_chat_completion(system or '', prompt, max_tokens=600)
        initial_ai = json.loads(resp)
    except:
        initial_ai = {
            "synthesis": "The archive is open. Present your first recollection.",
            "kaleidoscope_config": {"sides": 6, "primary_color": "Silver", "fractal_type": "Crystalline"},
            "next_recollection": "The earliest light you remember."
        }

    initial_state = {
        "theme": req.theme,
        "memories": [],
        "clarity": 10,
        "resonance": 50,
        "hue": "#FFFFFF",
        "cluster": "The Awakening",
        "kaleidoscope_config": initial_ai.get("kaleidoscope_config"),
        "last_synthesis": initial_ai.get("synthesis"),
        "next_prompt": initial_ai.get("next_recollection"),
        "visual_prompt": initial_ai.get("visual_prompt"),
        "turn": 1,
        "ai_enabled": req.ai_enabled,
        "last_ai_response": initial_ai
    }
    
    session = await gm.create_session(game_slug=slug, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Fragment"})
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    return {'ok': True, 'session_id': session.session_id, 'group_id': group_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    memories = list(s.get("memories", []))
    memories.append({"user": req.user_id, "text": req.content, "timestamp": "now"})
        
    system_prompt = load_system_prompt(GAME_SLUG)
    observer_note = ""
    if session.analysis and req.user_id in session.analysis:
        p_analysis = session.analysis[req.user_id]
        if p_analysis.get("truth_mismatch_detected"):
            observer_note = f"\n[SHADOW OBSERVER: {p_analysis.get('fun_commentary')}]"

    context = f"""
    THE ARCHIVE:
    - Theme: {s.get('theme')}
    - Clarity: {s.get('clarity')} | Resonance: {s.get('resonance')}
    - Active Cluster: {s.get('cluster')}
    - Last Synthesis: {s.get('last_synthesis')}
    
    NEW FRAGMENT: {req.content} {observer_note}
    
    Synthesize the fragment. Return VALID JSON.
    Include [METADATA: clarity+X, resonance+X, hue=#HEX, cluster=Name] in 'synthesis'.
    """
    
    resp_str = await safe_chat_completion(system_prompt, context, max_tokens=800)
    try:
        ai_response = json.loads(resp_str)
    except:
        ai_response = {"synthesis": "The mosaic expands in silence.", "next_recollection": "Continue sharing."}
             
    # Parse Metadata
    import re
    new_clarity = s.get('clarity', 10)
    new_resonance = s.get('resonance', 50)
    new_hue = s.get('hue', "#FFFFFF")
    new_cluster = s.get('cluster', "General")
    
    synthesis_text = ai_response.get("synthesis", "")
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', synthesis_text)
    if meta_match:
        synthesis_text = synthesis_text.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("clarity"):
                try: new_clarity = min(100, max(0, new_clarity + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("resonance"):
                try: new_resonance = min(100, max(0, new_resonance + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("hue="):
                new_hue = up[4:]
            elif up.startswith("cluster="):
                new_cluster = up[8:]

    new_state = {
        **s,
        "memories": memories[-20:],
        "clarity": new_clarity,
        "resonance": new_resonance,
        "hue": new_hue,
        "cluster": new_cluster,
        "kaleidoscope_config": ai_response.get("kaleidoscope_config", s.get("kaleidoscope_config")),
        "last_synthesis": synthesis_text,
        "next_prompt": ai_response.get("next_recollection"),
        "visual_prompt": ai_response.get("visual_prompt"),
        "last_ai_response": {**ai_response, "synthesis": synthesis_text},
        "turn": s.get("turn", 0) + 1
    }
    
    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "content": req.content})
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
