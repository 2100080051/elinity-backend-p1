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

GAME_SLUG = 'ai-puzzle-architect'

class StartReq(BaseModel):
    user_id: str
    theme: Optional[str] = "Geometric Core"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    system = load_system_prompt(GAME_SLUG)
    
    prompt = f"Initialize the Puzzle Dimension with theme: {req.theme}. Present the first logical node."
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=500)
    
    try:
        data = json.loads(resp_str)
    except:
        data = {
            "narrative": "The void is waiting for structure. A single logic node hums in the center.",
            "builder_data": {"logic_flow": 10, "assembly_progress": 0, "complexity": "Basic"},
            "available_nodes": ["Activate node", "Analyze structure"]
        }

    initial_state = {
        "scene": data.get("narrative"),
        "logic_flow": 10,
        "assembly": 0,
        "complexity": "Basic",
        "nodes": data.get("available_nodes", []),
        "available_actions": data.get("available_nodes", []),
        "status": "active",
        "turn": 1
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Architect"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    system = load_system_prompt(GAME_SLUG)
    
    context = f"""
    STRUCTURE STATE:
    - Logic Flow: {s.get('logic_flow')}% | Assembly Progress: {s.get('assembly')}%
    - Complexity: {s.get('complexity')}
    - Active Nodes: {", ".join(s.get('nodes', []))}
    
    ARCHITECT INPUT: {req.action}
    """
    
    resp_str = await safe_chat_completion(system or '', context, temperature=0.7, max_tokens=800)
    try:
        data = json.loads(resp_str)
    except:
        data = {"narrative": "The logic is fragmented. Static interference detected.", "builder_data": s.get('builder_data')}

    # Metadata Parsing
    narrative = data.get("narrative", "")
    new_logic = s.get("logic_flow", 10)
    new_assembly = s.get("assembly", 0)
    
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative)
    if meta_match:
        narrative = narrative.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("logic"):
                try: new_logic = min(100, max(0, new_logic + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("assembly"):
                try: new_assembly = min(100, max(0, new_assembly + int(re.search(r'[-+]?\d+', up).group())))
                except: pass

    new_state = {
        **s,
        "scene": narrative,
        "logic_flow": new_logic,
        "assembly": new_assembly,
        "nodes": data.get("available_nodes", []),
        "available_actions": data.get("available_nodes", []),
        "turn": s.get("turn", 0) + 1
    }
    
    if new_assembly >= 100:
        new_state["status"] = "constructed"
        new_state["scene"] += "\n\nSTRUCTURE COMPLETED. THE LOGIC FLOW IS MONUMENTAL."

    updated_session = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": req.action, "result": narrative})
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    return {'ok': True, 'state': session.state, 'players': session.players}
