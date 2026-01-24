from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

class StartReq(BaseModel):
    user_id: Optional[str] = "anon"
    theme: Optional[str] = "FANTASY_RUINS"

class JoinReq(BaseModel):
    session_id: str
    user_id: str
    role: Optional[str] = "Adventurer"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    """Initialize a new persistent game session."""
    gm = GameManager(db)
    slug = 'ai-adventure-dungeon'
    system = load_system_prompt(slug)
    
    # 1. AI initialization
    prompt = f'Theme: {req.theme}. The dungeon breathes. Generate the first room and its metadata. [FORMAT: JSON]'
    try:
        resp = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=600)
        initial_ai = json.loads(resp)
    except:
        initial_ai = {
            "narrative": "You wake up in a stone chamber. Moist air clings to your skin.",
            "room_data": {"type": "Threshold", "threat_level": 1},
            "available_actions": ["Search the sarcophagus", "Inspect the iron door"],
            "atmosphere": "Eerie Calm"
        }
    
    initial_state = {
        "scene": initial_ai.get("narrative"), 
        "narrative": initial_ai.get("narrative"),
        "theme": req.theme,
        "floor": 1,
        "hp": 100,
        "ap": 100,
        "xp": 0,
        "level": 1,
        "inventory": ["Rusted Sword", "Torch"],
        "gold": 10,
        "room_data": initial_ai.get("room_data", {}),
        "available_actions": initial_ai.get("available_actions", []),
        "atmosphere": initial_ai.get("atmosphere", "Neutral"),
        "visual_cue": initial_ai.get("visual_cue"),
        "turn": 1,
        "status": "active" 
    }
    
    session = await gm.create_session(game_slug=slug, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Seeker"})
    
    return {'ok': True, 'session_id': session.session_id, 'state': session.state, 'players': session.players}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
        
    s = session.state
    slug = 'ai-adventure-dungeon'
    system = load_system_prompt(slug)
    
    # Construct history context (last 8 interactions)
    history_context = ""
    if session.history:
        recent = session.history[-8:]
        history_context = "\n".join([f"Action: {h.get('content')}\nResult: {h.get('result')}" for h in recent])

    prompt = f"""
    THE CHRONICLE:
    {history_context}
    
    CURRENT ENTITY:
    - Level {s.get('level')} Explorer
    - HP: {s.get('hp')} | AP: {s.get('ap')} | XP: {s.get('xp')}
    - Gold: {s.get('gold')}
    - Inventory: {", ".join(s.get('inventory', []))}
    - Room Type: {s.get('room_data', {}).get('type')}
    
    PLAYER INTENT: {req.action}
    
    Narrate the consequence and the next room. Return VALID JSON.
    Include [METADATA: hp+X, ap+X, xp+X, gold+X, item+Name] in 'narrative'.
    """
    
    resp_str = await safe_chat_completion(system or '', prompt, temperature=0.7, max_tokens=800)
    try:
        ai_response = json.loads(resp_str)
    except:
        ai_response = {"narrative": "The dungeon shifts. You find yourself in a new hallway.", "phase": "Exploration", "available_actions": ["Move forward"]}
    
    # Parse Metadata
    import re
    new_hp = s.get('hp', 100)
    new_ap = s.get('ap', 100)
    new_xp = s.get('xp', 0)
    new_gold = s.get('gold', 0)
    new_inv = list(s.get('inventory', []))
    
    narrative_text = ai_response.get("narrative", "")
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative_text)
    if meta_match:
        narrative_text = narrative_text.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("hp"):
                try: new_hp = min(100, max(0, new_hp + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("ap"):
                try: new_ap = min(100, max(0, new_ap + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("xp"):
                try: new_xp += int(re.search(r'\d+', up).group())
                except: pass
            elif up.startswith("gold"):
                try: new_gold = max(0, new_gold + int(re.search(r'[-+]?\d+', up).group()))
                except: pass
            elif up.startswith("item+"):
                new_inv.append(up[5:])
            elif up.startswith("item-"):
                it = up[5:]
                if it in new_inv: new_inv.remove(it)

    # Level Up check
    new_level = s.get('level', 1)
    if new_xp >= 100:
        new_level += 1
        new_xp -= 100
        new_hp = 100 # Reset hp on level up
        new_ap = 100 # Reset ap on level up

    new_state = {
        **s,
        "scene": narrative_text,
        "narrative": narrative_text,
        "hp": new_hp,
        "ap": new_ap,
        "xp": new_xp,
        "level": new_level,
        "gold": new_gold,
        "inventory": new_inv,
        "room_data": ai_response.get("room_data", {}),
        "available_actions": ai_response.get("available_actions", []),
        "atmosphere": ai_response.get("atmosphere", s.get("atmosphere")),
        "visual_cue": ai_response.get("visual_cue"),
        "last_ai_response": {**ai_response, "narrative": narrative_text},
        "turn": s.get("turn", 0) + 1
    }
    
    updated_session = await gm.update_state(
        req.session_id, 
        new_state, 
        history_entry={"user": req.user_id, "action": "action", "content": req.action, "result": narrative_text}
    )
    
    return {'ok': True, 'state': updated_session.state, 'history': updated_session.history}

@router.get('/status/{session_id}')
async def status(session_id: str, db: AsyncSession = Depends(get_async_db)):
    """Poll for latest state."""
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    return {'ok': True, 'state': session.state, 'players': session.players, 'history': session.history}
