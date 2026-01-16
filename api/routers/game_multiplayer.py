from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from .game_session_manager import GameManager
from database.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.token import get_optional_user
from models.user import Tenant

import json
import uuid

router = APIRouter(tags=["Multiplayer"])

class CreateRoomReq(BaseModel):
    game_slug: str
    user_id: Optional[str] = None  # For guest support
    max_players: Optional[int] = 5

class JoinRoomReq(BaseModel):
    room_code: str
    user_id: Optional[str] = None  # For guest support
    truth_analysis_enabled: Optional[bool] = False
    persona: Optional[str] = None

class PlayerStatusReq(BaseModel):
    session_id: str
    user_id: Optional[str] = None  # For guest support
    is_ready: bool
    truth_analysis_enabled: Optional[bool] = None
    persona: Optional[str] = None

class ChatMessageReq(BaseModel):
    session_id: str
    user_id: Optional[str] = None  # For guest support
    message: str
    sender_name: Optional[str] = None

@router.post("/create")
async def create_room(req: CreateRoomReq, user: Optional[Tenant] = Depends(get_optional_user), db: AsyncSession = Depends(get_async_db)):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        gm = GameManager(db)
        
        # Handle guest user automatically if not logged in
        user_id = user.id if user else req.user_id
        if not user_id:
            user_id = f"guest_{uuid.uuid4().hex[:8]}"
        logger.info(f"🎮 Creating room for user: {user_id}, game: {req.game_slug}")
        
        if not user:
            from utils.guest_manager import ensure_guest_user
            logger.info(f"Creating guest user {user_id}...")
            await ensure_guest_user(db, user_id)
          
        session = await gm.create_session(req.game_slug, host_id=user_id, max_players=req.max_players)
        
        # Automatically join as host
        await gm.join_session(session.session_id, user_id, {
            "name": user.email.split('@')[0] if user else f"Guest_{user_id[-4:]}", 
            "role": "Host",
            "truth_analysis_enabled": False,
            "persona": "The Architect"
        })
        
        logger.info(f"✅ Successfully created room {session.room_code} for {user_id}")
        return {"ok": True, "session_id": session.session_id, "room_code": session.room_code, "is_guest": not user, "user_id": user_id}
    
    except Exception as e:
        logger.error(f"❌ Error creating room: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")

@router.post("/join")
async def join_room(req: JoinRoomReq, user: Optional[Tenant] = Depends(get_optional_user), db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(room_code=req.room_code.upper())
    if session.status != "lobby":
        raise HTTPException(status_code=400, detail="Game already started")
    
    # Handle guest user automatically - prioritze ID from frontend if guest
    user_id = user.id if user else req.user_id
    if not user_id:
        user_id = f"guest_{uuid.uuid4().hex[:8]}"
        
    if not user:
         from utils.guest_manager import ensure_guest_user
         await ensure_guest_user(db, user_id)

    await gm.join_session(session.session_id, user_id, {
        "name": user.email.split('@')[0] if user else f"Guest_{user_id[-4:]}", 
        "role": "Player",
        "truth_analysis_enabled": req.truth_analysis_enabled,
        "persona": req.persona or "The Voyager"
    })
    return {"ok": True, "session_id": session.session_id, "game_slug": session.game_slug, "is_guest": not user, "user_id": user_id}

@router.post("/ready")
async def toggle_ready(req: PlayerStatusReq, user: Optional[Tenant] = Depends(get_optional_user), db: AsyncSession = Depends(get_async_db)):
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Ready Toggle Req: {req}")
    logger.info(f"Auth User: {user.id if user else 'None'}")

    # Get user_id from authenticated user or from request (for guests)
    target_user_id = user.id if user else req.user_id
    logger.info(f"Target User ID: {target_user_id}")
    
    if not target_user_id:
        logger.error("400: user_id required for guests")
        raise HTTPException(status_code=400, detail="user_id required for guests")

    gm = GameManager(db)
    # Update both ready status and fun-mode toggle
    session = await gm.update_player_status(
        req.session_id, 
        target_user_id, 
        req.is_ready, 
        req.truth_analysis_enabled,
        req.persona
    )
    logger.info(f"Status Updated. Current Players: {list(session.players.keys())}")
    return {"ok": True, "players": session.players}

@router.post("/chat")
async def send_chat_message(req: ChatMessageReq, user: Optional[Tenant] = Depends(get_optional_user), db: AsyncSession = Depends(get_async_db)):
    """Send a chat message to the game session lobby."""
    target_user_id = user.id if user else req.user_id
    sender_name = req.sender_name or (user.email.split('@')[0] if user else f"Guest_{target_user_id[-4:] if target_user_id else 'Unknown'}")
    
    if not target_user_id:
        raise HTTPException(status_code=400, detail="user_id required for guests")

    gm = GameManager(db)
    session = await gm.get_session(req.session_id)
    
    # Get current chat messages or initialize
    state = dict(session.state or {})
    chat_messages = state.get("chat_messages", [])
    
    import datetime
    # Add new message
    new_message = {
        "user_id": target_user_id,
        "sender": sender_name,
        "message": req.message,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    chat_messages.append(new_message)
    
    # Keep only last 100 messages
    if len(chat_messages) > 100:
        chat_messages = chat_messages[-100:]
    
    # Update state with new messages
    await gm.update_state(req.session_id, {"chat_messages": chat_messages})
    
    return {"ok": True, "message": new_message, "total_messages": len(chat_messages)}

@router.post("/start/{session_id}")
async def start_game(session_id: str, user: Optional[Tenant] = Depends(get_optional_user), db: AsyncSession = Depends(get_async_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Host authentication required")
        
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    if session.host_user_id != user.id:
        raise HTTPException(status_code=403, detail="Only host can start the game")
    
    # Check minimum 1 players (host)
    players = session.players or {}
    MIN_PLAYERS = 1
    if len(players) < MIN_PLAYERS:
        raise HTTPException(status_code=400, detail=f"Need at least {MIN_PLAYERS} players to start. Currently have {len(players)}.")

    # GAME INITIALIZATION
    # We must generate the initial state here so all players land in a "ready" game.
    from ._system_prompt import load_system_prompt
    from ._llm import safe_chat_completion
    
    slug = session.game_slug or 'story-weaver'
    system = load_system_prompt(slug)
    
    # Determine theme/prompt based on slug/category (Generic fallback works for 60+ games)
    prompt = f"Generate a short, engaging opening scene/narrative for a game of '{slug}' in 2-3 sentences. End with a call to action."
    fallback = "The adventure begins. What will you do?"
    
    # Generate Opening
    opening_text = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=250, fallback=fallback)
    
    # 1. Update State
    initial_state = dict(session.state or {})
    initial_state.update({
        "narrative": opening_text,
        "scene": opening_text, # Backward compat
        "story_text": [opening_text], # For narrative games
        "turn": 1,
        "status": "active", # Internal state logic
        "active_player": list(players.keys())[0] if players else None # Simple turn init
    })
    
    session.state = initial_state
    session.status = "active" # DB Status Column -> Triggers Frontend Redirect
    
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(session, "state")
    
    await db.commit()
    await db.refresh(session)
    
    return {"ok": True, "player_count": len(players), "state": session.state}

@router.get("/session/{session_id}")
async def get_room_details(session_id: str, db: AsyncSession = Depends(get_async_db)):
    gm = GameManager(db)
    session = await gm.get_session(session_id)
    state = dict(session.state or {})
    state['history'] = session.history or [] # Inject history for frontend visibility

    
    # NEW: Try to find the associated chat group_id
    from models.chat import Group
    group_name = f"game_{session_id}"
    result = await db.execute(select(Group).where(Group.name == group_name))
    group = result.scalars().first()
    
    return {
        "ok": True, 
        "session_id": session.session_id,
        "room_code": session.room_code,
        "status": session.status,
        "players": session.players,
        "host_id": session.host_user_id,
        "game_slug": session.game_slug,
        "analysis": session.analysis,
        "state": state,  # CRITICAL: Return full game state for multiplayer sync
        "history": session.history or [], # NEW: Return history event log
        "chat_messages": state.get("chat_messages", []),
        "group_id": group.id if group else session_id,  # Fallback to session_id
        "min_players": 1
    }

@router.get("/list")
async def get_all_games():
    """Returns a comprehensive list of all verified games, separated by tier."""
    
    # The Core 10 Premium Games
    premium_games = [
        {"slug": 'story-weaver', "name": 'The Story Weaver', "tier": 'premium', "category": 'Narrative', "image": 'https://images.unsplash.com/photo-1519074069444-1ba4fff66d16'},
        {"slug": 'myth-maker', "name": 'Myth Maker Arena', "tier": 'premium', "category": 'Adventure', "image": 'https://images.unsplash.com/photo-1614726365723-49cfae9e95bc'},
        {"slug": 'world-builders', "name": 'World Builders', "tier": 'premium', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1451187580459-43490279c0fa'},
        {"slug": 'truth-layer', "name": 'Truth & Layer', "tier": 'premium', "category": 'Social', "image": 'https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d'},
        {"slug": 'memory-mosaic', "name": 'Memory Mosaic', "tier": 'premium', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1506744038136-46273834b3fb'},
        {"slug": 'alignment-game', "name": 'The Alignment Game', "tier": 'premium', "category": 'Strategy', "image": 'https://images.unsplash.com/photo-1555680202-c86f0e12f086'},
        {"slug": 'compass-game', "name": 'The Compass Game', "tier": 'premium', "category": 'Self-Discovery', "image": 'https://images.unsplash.com/photo-1501504905252-473c47e087f8'},
        {"slug": 'echoes', "name": 'Echoes & Expressions', "tier": 'premium', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1514525253440-b393452e3383'},
        {"slug": 'serendipity', "name": 'Serendipity Strings', "tier": 'premium', "category": 'Social', "image": 'https://images.unsplash.com/photo-1528459801416-a9e53bbf4e05'},
        {"slug": 'long-quest', "name": 'The Long Quest', "tier": 'premium', "category": 'Adventure', "image": 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23'},
    ]

    # The Standard Library (Sample - functionality upgraded)
    standard_games = [
        {"slug": 'ai-adventure-dungeon', "name": 'AI Adventure Dungeon', "tier": 'standard', "category": 'RPG', "image": 'https://images.unsplash.com/photo-1533613220915-609f661a6fe1'},
        {"slug": 'ai-comic-creator', "name": 'AI Comic Creator', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe'},
        {"slug": 'ai-emoji-war', "name": 'AI Emoji War', "tier": 'standard', "category": 'Action', "image": 'https://images.unsplash.com/photo-1541701494587-cb58502866ab'},
        {"slug": 'ai-escape-room', "name": 'AI Escape Room', "tier": 'standard', "category": 'Puzzle', "image": 'https://images.unsplash.com/photo-1519074069444-1ba4fff66d16'},
        {"slug": 'ai-fortune-teller', "name": 'AI Fortune Teller', "tier": 'standard', "category": 'Mystic', "image": 'https://images.unsplash.com/photo-1530519729491-aea5b51d1ee1'},
        {"slug": 'ai-improv-theater', "name": 'AI Improv Theater', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1503095392237-73621405b0c9'},
        {"slug": 'ai-poetry-garden', "name": 'AI Poetry Garden', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1490750967868-58cb75069faf'},
        {"slug": 'ai-puzzle-architect', "name": 'AI Puzzle Architect', "tier": 'standard', "category": 'Puzzle', "image": 'https://images.unsplash.com/photo-1535905557558-afc4877a26fc'},
        {"slug": 'ai-puzzle-saga', "name": 'AI Puzzle Saga', "tier": 'standard', "category": 'Puzzle', "image": 'https://images.unsplash.com/photo-1588196843460-b74737aa36aa'},
        {"slug": 'ai-rap-battle', "name": 'AI Rap Battle', "tier": 'standard', "category": 'Music', "image": 'https://images.unsplash.com/photo-1516280440614-6697288d5d38'},
        {"slug": 'ai-roast-toast', "name": 'AI Roast Toast', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1595152772835-219674b2a8a6'},
        {"slug": 'ai-role-swap', "name": 'AI Role Swap', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1563823251941-b998f8287893'},
        {"slug": 'ai-sandbox', "name": 'AI Sandbox', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1605810230434-7631ac76ec81'},
        {"slug": 'character-swap', "name": 'Character Swap', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61'},
        {"slug": 'collaborative-canvas', "name": 'Collaborative Canvas', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1513364776144-60967b0f800f'},
        {"slug": 'connection-sparks', "name": 'Connection Sparks', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1521791136064-7986c2920216'},
        {"slug": 'creative-duel-arena', "name": 'Creative Duel Arena', "tier": 'standard', "category": 'Action', "image": 'https://images.unsplash.com/photo-1605810230434-7631ac76ec81'},
        {"slug": 'cultural-exchange', "name": 'Cultural Exchange', "tier": 'standard', "category": 'Education', "image": 'https://images.unsplash.com/photo-1528642474498-1af0c17fd8c3'},
        {"slug": 'dream-battles', "name": 'Dream Battles', "tier": 'standard', "category": 'Action', "image": 'https://images.unsplash.com/photo-1493246507139-91e8fad9978e'},
        {"slug": 'dream-builder', "name": 'Dream Builder', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1496382411466-254ad0dac2a3'},
        {"slug": 'emotion-charades', "name": 'Emotion Charades', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1509315811345-672d83ef2fbc'},
        {"slug": 'emotion-labyrinth', "name": 'Emotion Labyrinth', "tier": 'standard', "category": 'Self-Discovery', "image": 'https://images.unsplash.com/photo-1470252649378-9c29740c9fa8'},
        {"slug": 'epic-poem-duel', "name": 'Epic Poem Duel', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1519681393784-d8e5b5a45742'},
        {"slug": 'friendship-towers', "name": 'Friendship Towers', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1523240795612-9a054b0db644'},
        {"slug": 'future-artifact-maker', "name": 'Future Artifact Maker', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158'},
        {"slug": 'future-forecast', "name": 'Future Forecast', "tier": 'standard', "category": 'Strategy', "image": 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b'},
        {"slug": 'gratitude-quest', "name": 'Gratitude Quest', "tier": 'standard', "category": 'Wellbeing', "image": 'https://images.unsplash.com/photo-1507434965515-61970f2bd7c6'},
        {"slug": 'great-debate', "name": 'Great Debate', "tier": 'standard', "category": 'Strategy', "image": 'https://images.unsplash.com/photo-1524178232363-1fb2b075b955'},
        {"slug": 'guess-the-fake', "name": 'Guess The Fake', "tier": 'standard', "category": 'Puzzle', "image": 'https://images.unsplash.com/photo-1563206767-5b1d972e8136'},
        {"slug": 'hidden-truths', "name": 'Hidden Truths', "tier": 'standard', "category": 'Mystery', "image": 'https://images.unsplash.com/photo-1519074069444-1ba4fff66d16'},
        {"slug": 'inner-world-quest', "name": 'Inner World Quest', "tier": 'standard', "category": 'Self-Discovery', "image": 'https://images.unsplash.com/photo-1518531933037-91b2f5f229cc'},
        {"slug": 'journey-journal', "name": 'Journey Journal', "tier": 'standard', "category": 'Wellbeing', "image": 'https://images.unsplash.com/photo-1544376798-89aa6b82c6cd'},
        {"slug": 'journey-through-music', "name": 'Journey Through Music', "tier": 'standard', "category": 'Music', "image": 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4'},
        {"slug": 'legacy-builder', "name": 'Legacy Builder', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1461301214746-1e790926d323'},
        {"slug": 'life-goals-board-game', "name": 'Life Goals RPG', "tier": 'standard', "category": 'Strategy', "image": 'https://images.unsplash.com/photo-1432888622747-4eb9a8efeb07'},
        {"slug": 'life-swap-simulator', "name": 'Life Swap Simulator', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1557804506-669a67965ba0'},
        {"slug": 'meme-forge', "name": 'Meme Forge', "tier": 'standard', "category": 'Fun', "image": 'https://images.unsplash.com/photo-1531251445707-1f000e1e87d0'},
        {"slug": 'micro-mysteries', "name": 'Micro Mysteries', "tier": 'standard', "category": 'Mystery', "image": 'https://images.unsplash.com/photo-1478720568477-152d9b164e63'},
        {"slug": 'mind-meld', "name": 'Mind Meld', "tier": 'standard', "category": 'Social', "image": 'https://images.unsplash.com/photo-1573164713714-d95e436ab8d6'},
        {"slug": 'mood-dj', "name": 'Mood DJ', "tier": 'standard', "category": 'Music', "image": 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745'},
        {"slug": 'mood-journey', "name": 'Mood Journey', "tier": 'standard', "category": 'Wellbeing', "image": 'https://images.unsplash.com/photo-1604881991720-f91add269bed'},
        {"slug": 'mood-mosaic', "name": 'Mood Mosaic', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1496715976403-7e36dc43f17b'},
        {"slug": 'myth-builder', "name": 'Myth Builder', "tier": 'standard', "category": 'Creative', "image": 'https://images.unsplash.com/photo-1478720568477-152d9b164e63'},
    ]
    
    # Combined list
    return {"ok": True, "games": premium_games + standard_games}

@router.get("/my-games")
async def get_my_games(user_id: Optional[str] = None, user: Optional[Tenant] = Depends(get_optional_user), db: AsyncSession = Depends(get_async_db)):
    """List all active or valid game sessions for the user."""
    target_user_id = user.id if user else user_id
    if not target_user_id:
        # If no user ID provided and not logged in, return empty
        return {"ok": True, "games": []}
    
    from models.game_session import GameSession
    
    # We have to fetch all sessions and filter in python because 'players' is JSONB
    # Optimization: Filter by host_user_id OR just fetch recent ones. 
    # For now, fetch all active/lobby sessions.
    
    result = await db.execute(
        select(GameSession)
        .where(GameSession.status.in_(["lobby", "active"]))
        .order_by(GameSession.created_at.desc())
        .limit(50) 
    )
    all_sessions = result.scalars().all()
    
    my_games = []
    for s in all_sessions:
        players = s.players or {}
        if target_user_id in players:
            my_games.append({
                "session_id": s.session_id,
                "game_slug": s.game_slug,
                "room_code": s.room_code,
                "created_at": s.created_at,
                "status": s.status,
                "player_count": len(players)
            })
            
    return {"ok": True, "games": my_games, "user_id": target_user_id}
