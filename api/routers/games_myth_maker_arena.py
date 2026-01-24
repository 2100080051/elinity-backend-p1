from fastapi import APIRouter, Depends, HTTPException
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
GAME_SLUG = "elinity-myth-maker-arena"

class StartReq(BaseModel):
    user_id: str
    archetype: Optional[str] = "Warrior"
    ai_enabled: Optional[bool] = True

class JoinReq(BaseModel):
    session_id: str
    user_id: str
    archetype: Optional[str] = "Seer"

class ActionReq(BaseModel):
    session_id: str
    user_id: str
    action: str 
    content: str 

@router.post('/start')
async def start(req: StartReq, db: AsyncSession = Depends(get_async_db)):
    # Ensure user exists
    from utils.guest_manager import ensure_guest_user
    await ensure_guest_user(db, req.user_id)
    
    gm = GameManager(db)
    system_prompt = load_system_prompt(GAME_SLUG)
    
    initial_ai = {}
    if req.ai_enabled:
        prompt = f"Initialize the Stellar Chronicle. Hero: {req.archetype}. The stars are waiting. Weave the first constellation. [FORMAT: JSON]"
        try:
            resp = await safe_chat_completion(system_prompt, prompt, max_tokens=600)
            initial_ai = json.loads(resp)
        except:
             initial_ai = {
                "narrative": "A mortal spark ignites in the void. Believers begin to whisper your name.",
                "mythic_card": {"title": "The Spark", "prophecy": "From nothing, everything."},
                "constellation_status": "Mortal Spark",
                "divine_options": [{"concept": "Search for power", "cost": "0", "benefit": "Gains divinity"}]
            }

    initial_state = {
        "narrative": initial_ai.get("narrative"),
        "archetype": req.archetype,
        "belief": 10,
        "divinity": 0,
        "starsigns": [],
        "favor_architect": 0,
        "favor_catalyst": 0,
        "favor_witness": 0,
        "constellation_status": initial_ai.get("constellation_status", "Genesis"),
        "mythic_card": initial_ai.get("mythic_card", {}),
        "divine_options": initial_ai.get("divine_options", []),
        "myth_log": [initial_ai],
        "turn": 1,
        "ai_enabled": req.ai_enabled,
        "last_ai_response": initial_ai
    }
    
    session = await gm.create_session(game_slug=GAME_SLUG, host_id=req.user_id, initial_state=initial_state)
    await gm.join_session(session.session_id, req.user_id, {"role": "Demi-God", "archetype": req.archetype})
    group_id = await create_game_chat_group(db, session.session_id, req.user_id)
    return {'ok': True, 'session_id': session.session_id, 'group_id': group_id, 'state': session.state}

@router.post('/action')
async def action(req: ActionReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    
    s = session.state
    myth_log = list(s.get("myth_log", []))
    
    ai_response = {}
    system_prompt = load_system_prompt(GAME_SLUG)
    
    observer_note = ""
    if session.analysis and req.user_id in session.analysis:
        p_analysis = session.analysis[req.user_id]
        if p_analysis.get("truth_mismatch_detected"):
            observer_note = f"\n[SHADOW OBSERVER: {p_analysis.get('fun_commentary')}]"

    context = f"""
    THE STELLAR CHRONICLE:
    - Status: {s.get('constellation_status')}
    - Belief: {s.get('belief')} | Divinity: {s.get('divinity')}
    - Starsigns: {", ".join(s.get('starsigns', []))}
    - Favors: Architect={s.get('favor_architect')}, Catalyst={s.get('favor_catalyst')}, Witness={s.get('favor_witness')}
    
    PREV NARRATIVE: {s.get('narrative')}
    DEITY'S ACT: {req.content} {observer_note}
    
    Continue the myth. Return VALID JSON.
    Include [METADATA: belief+X, divinity+X, starsign=Name, favor_architect+X, favor_catalyst+X, favor_witness+X] in 'narrative'.
    """
    
    resp_str = await safe_chat_completion(system_prompt, context, max_tokens=800)
    try:
        ai_response = json.loads(resp_str)
    except:
        ai_response = {"narrative": "A great silence falls over the stars.", "constellation_status": "Stasis"}
             
    # Parse Metadata
    import re
    new_belief = s.get('belief', 10)
    new_divinity = s.get('divinity', 0)
    new_starsigns = list(s.get('starsigns', []))
    new_f_a = s.get('favor_architect', 0)
    new_f_c = s.get('favor_catalyst', 0)
    new_f_w = s.get('favor_witness', 0)
    
    narrative_text = ai_response.get("narrative", "")
    meta_match = re.search(r'\[METADATA:\s*(.*?)\]', narrative_text)
    if meta_match:
        narrative_text = narrative_text.replace(meta_match.group(0), "").strip()
        updates = meta_match.group(1).split(",")
        for up in updates:
            up = up.strip()
            if up.startswith("belief"):
                try: new_belief = min(100, max(0, new_belief + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("divinity"):
                try: new_divinity = min(100, max(0, new_divinity + int(re.search(r'[-+]?\d+', up).group())))
                except: pass
            elif up.startswith("starsign="):
                new_starsigns.append(up[9:])
            elif up.startswith("favor_architect"):
                try: new_f_a += int(re.search(r'[-+]?\d+', up).group())
                except: pass
            elif up.startswith("favor_catalyst"):
                try: new_f_c += int(re.search(r'[-+]?\d+', up).group())
                except: pass
            elif up.startswith("favor_witness"):
                try: new_f_w += int(re.search(r'[-+]?\d+', up).group())
                except: pass

    if ai_response:
        ai_response["narrative"] = narrative_text
        myth_log.append(ai_response)

    new_state = {
        **s,
        "belief": new_belief,
        "divinity": new_divinity,
        "starsigns": list(set(new_starsigns))[-5:],
        "favor_architect": new_f_a,
        "favor_catalyst": new_f_c,
        "favor_witness": new_f_w,
        "narrative": narrative_text,
        "mythic_card": ai_response.get("mythic_card", s.get("mythic_card")),
        "constellation_status": ai_response.get("constellation_status", s.get("constellation_status")),
        "divine_options": ai_response.get("divine_options", []),
        "myth_log": myth_log[-10:],
        "last_ai_response": ai_response,
        "turn": s.get("turn", 0) + 1
    }
    
    updated = await gm.update_state(req.session_id, new_state, history_entry={"user": req.user_id, "action": "action", "content": req.content})
    return {'ok': True, 'state': updated.state}

@router.post('/join')
async def join(req: JoinReq, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.join_session(req.session_id, req.user_id, {"role": "Demi-God", "archetype": req.archetype})
    from models.chat import Group
    group_name = f"game_{req.session_id}"
    result = await db.execute(select(Group).where(Group.name == group_name))
    group = result.scalars().first()
    if group: await add_player_to_game_chat(db, group.id, req.user_id)
    return {'ok': True, 'players': session.players, 'group_id': group.id if group else None}
