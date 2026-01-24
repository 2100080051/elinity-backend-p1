from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import re
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

GAME_SLUG = 'ai-guess-the-fake'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "The Midnight Heist"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Interrogation with case theme: {req.theme}. Present the three claims."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The light flickers. Three files are slid across the table. One is a fabrication.",
            "fake_data": {"bullshit_level": 10, "current_case": req.theme, "identified_fake": False},
            "available_moves": ["Examine File Alpha", "Question the suspect"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "suspicion": 10,
        "case": req.theme,
        "stress": 10,
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Interrogator"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    INTERROGATION STATE:
    - Suspicion Level: {s.get('suspicion')}% | Stress Index: {s.get('stress')}%
    - Current Case: {s.get('case')}
    
    INTERROGATOR MOVE: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The suspect remains silent. The clock is ticking.", "fake_data": s.get('fake_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_suspicion = s.get("suspicion", 10)
    new_stress = s.get("stress", 10)
    new_case = s.get("case", "")
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("suspicion"):
                try: new_suspicion = min(100, max(0, new_suspicion + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("stress"):
                try: new_stress = min(100, max(0, new_stress + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("case"):
                new_case = up[5:]

    new_state = {
        **s,
        "scene": narrative,
        "suspicion": new_suspicion,
        "stress": new_stress,
        "case": new_case,
        "moves": data.get("available_moves", []),
        "available_actions": data.get("available_moves", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if "GUESS CORRECT" in narrative.upper():
        new_state["status"] = "solved"
        new_state["scene"] += "\n\nCRACKED. THE FAKE HAS BEEN EXPOSED."
    elif new_stress >= 100:
        new_state["status"] = "failed"
        new_state["scene"] += "\n\nINTERROGATION FAILED. THE SUSPECT WALKED."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
