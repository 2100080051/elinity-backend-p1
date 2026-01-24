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
GAME_SLUG = "elinity-truth-and-layer"

class StartReq(BaseModel):
    user_id: str
    ai_enabled: Optional[bool] = True

class JoinReq(BaseModel):
    session_id: str
    user_id: str

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str # "answer", "skip"
    content: str 

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    # Ensure user exists
    from utils.guest_manager import ensure_guest_user
    await ensure_guest_user(db, req.user_id)
    
    gm = GameManager(db)
    system_prompt = load_system_prompt(GAME_SLUG)
    
    # Generate First Question
    initial_ai = {}
    if req.ai_enabled:
        prompt = "Initialize Layer 1: The Persona. Establish the first frequency. [FORMAT: JSON]"
        try:
            resp = await safe_chat_completion(system_prompt, prompt, max_tokens=600)
            initial_ai = json.loads(resp)
        except:
             initial_ai = {
                "aperture_question": "What mask do you wear most often in high-stress environments?", 
                "proxy_analysis": "Initial scan complete.", 
                "layer_status": {"current": 1, "title": "The Social Mirror"},
                "subliminal_prompt": "Reveal"
            } 

    initial_state = {
        "layer": 1,
        "layer_title": initial_ai.get("layer_status", {}).get("title", "The Persona"),
        "integrity": 100,
        "vulnerability": 10,
        "shielding": 50,
        "turn": 1,
        "current_question": initial_ai.get("aperture_question"),
        "proxy_analysis": initial_ai.get("proxy_analysis"),
        "visual_frequency": initial_ai.get("visual_frequency"),
        "subliminal_prompt": initial_ai.get("subliminal_prompt"),
        "ai_enabled": req.ai_enabled,
        "last_ai_response": initial_ai
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Probe Subject"})
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    return {'ok': True, 'session_id': session.session_id, 'group_id': group_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system_prompt = load_system_prompt(GAME_SLUG)
    
    observer_note = ""
    if session.analysis and req.user_id in session.analysis:
        p_analysis = session.analysis[req.user_id]
        if p_analysis.get("truth_mismatch_detected"):
            observer_note = f"\n[SHADOW OBSERVER: {p_analysis.get('fun_commentary')}]"

    context = f"""
    PROBE STATE:
    - Layer: {s.get('layer')} ({s.get('layer_title')})
    - Integrity: {s.get('integrity')}
    - Vulnerability: {s.get('vulnerability')}
    - Shielding: {s.get('shielding')}
    
    PREV QUESTION: {s.get('current_question')}
    SUBJECT RESPONSE: {req.content} {observer_note}
    
    Analyze the frequency. Return VALID JSON.
    Include [METADATA: integrity-X, vulnerability+X, shielding-X, layer+1] in 'proxy_analysis'.
    """
    
    resp_str = await safe_chat_completion(system_prompt, context, max_tokens=800)
    try:
        ai_response = json.loads(resp_str)
    except:
        ai_response = {"aperture_question": "Why do you resist?", "proxy_analysis": "Shielding too high."}
             
    # Parse Updates
    import re
    new_integ = s.get('integrity', 100)
    new_vuln = s.get('vulnerability', 10)
    new_shield = s.get('shielding', 50)
    new_layer = s.get('layer', 1)
    
    analysis_text = ai_response.get("proxy_analysis", "")
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', analysis_text)
    if meta_match:
        analysis_text = analysis_text.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("integrity"):
                try: new_integ = min(100, max(0, new_integ + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("vulnerability"):
                try: new_vuln = min(100, max(0, new_vuln + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("shielding"):
                try: new_shield = min(100, max(0, new_shield + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("layer+1"):
                new_layer = min(7, new_layer + 1)

    new_state = {
        **s,
        "layer": new_layer,
        "layer_title": ai_response.get("layer_status", {}).get("title", s.get("layer_title")),
        "integrity": new_integ,
        "vulnerability": new_vuln,
        "shielding": new_shield,
        "current_question": ai_response.get("aperture_question"),
        "proxy_analysis": analysis_text,
        "visual_frequency": ai_response.get("visual_frequency"),
        "subliminal_prompt": ai_response.get("subliminal_prompt"),
        "last_ai_response": {**ai_response, "proxy_analysis": analysis_text},
        "turn": s.get("turn", 0) + 1
    }
    
    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "answer": req.content})
    return {'ok': True, 'state': updated.state}

@router.post('/join')
async def join(req: JoinReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.join_session(req.session_id, req.user_id, {"role": "Player"})
    
    from models.chat import Group
    group_name = f"game_{req.session_id}"
    result = await db.execute(select(Group).where(Group.name == group_name))
    group = result.scalars().first()
    if group:
        await add_player_to_game_chat(db, group.id, req.user_id)
        
    return {'ok': True, 'players': session.players, 'group_id': group.id if group else None}
