from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.game_session import GameSession
from fastapi import HTTPException
from sqlalchemy.sql import func
import uuid

import random
import string

class GameManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_room_code(self, length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    async def ensure_tenant(self, user_id: str):
        """Ensures a tenant exists for the given user_id; creates a guest if not."""
        if not user_id: return
        
        from models.user import Tenant
        result = await self.db.execute(select(Tenant).where(Tenant.id == user_id))
        if not result.scalars().first():
            try:
                new_guest = Tenant(
                    id=user_id,
                    email=f"guest_{user_id}@elinity.ai", 
                    password="guest_password",
                    role="user"
                )
                self.db.add(new_guest)
                await self.db.flush() 
            except Exception as e:
                print(f"Failed to auto-create guest {user_id}: {e}")

    async def create_session(self, game_slug: str, host_id: str = None, initial_state: dict = None, max_players: int = 5):
        """Creates a new game session with a room code."""
        if host_id:
            await self.ensure_tenant(host_id)

        session_id = str(uuid.uuid4())
        room_code = self.generate_room_code()
        
        new_session = GameSession(
            session_id=session_id,
            room_code=room_code,
            game_slug=game_slug,
            host_user_id=host_id,
            status="lobby",
            max_players=max_players,
            state=initial_state or {},
            players={}
        )
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        return new_session

    async def get_session(self, session_id: str = None, room_code: str = None):
        """Retrieves a session by ID or Room Code."""
        if session_id:
            result = await self.db.execute(select(GameSession).where(GameSession.session_id == session_id))
        else:
            result = await self.db.execute(select(GameSession).where(GameSession.room_code == room_code))
            
        session = result.scalars().first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    async def join_session(self, session_id: str, user_id: str, user_data: dict = None):
        """Adds a player to the session with max player check."""
        await self.ensure_tenant(user_id)
        session = await self.get_session(session_id)
        
        players = dict(session.players or {})
        
        if user_id not in players:
            if len(players) >= (session.max_players or 5):
                raise HTTPException(status_code=400, detail="Room is full")
                
            import datetime
            players[user_id] = {
                **(user_data or {}),
                "joined_at": datetime.datetime.now().isoformat(),
                "is_ready": False,
                "score": 0
            }
            session.players = players
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(session, "players")
            
            await self.db.commit()
            await self.db.refresh(session)
            
        return session

    async def update_player_status(self, session_id: str, user_id: str, is_ready: bool, truth_analysis_enabled: bool = None, persona: str = None):
        """Updates player ready status and fun-mode preferences."""
        session = await self.get_session(session_id)
        players = dict(session.players or {})
        if user_id in players:
            players[user_id]["is_ready"] = is_ready
            if truth_analysis_enabled is not None:
                players[user_id]["truth_analysis_enabled"] = truth_analysis_enabled
            if persona:
                players[user_id]["persona"] = persona
                
            session.players = players
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(session, "players")
            await self.db.commit()
        return session

    async def start_game(self, session_id: str):
        """Sets session status to active."""
        session = await self.get_session(session_id)
        session.status = "active"
        await self.db.commit()
        return session

    async def update_state(self, session_id: str, new_state_patch: dict, history_entry: dict = None):
        """Updates the game state and optionally adds to history with AI analysis."""
        session = await self.get_session(session_id)
        
        current_state = dict(session.state or {})
        current_state.update(new_state_patch)
        session.state = current_state
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(session, "state")
        
        if history_entry:
            history = list(session.history or [])
            history.append(history_entry)
            session.history = history
            flag_modified(session, "history")
            
            # TRIGGER AI ANALYSIS
            try:
                from ._ai_observer import analyze_gameplay
                from ._profile_helper import get_user_profile_summary
                
                # Fetch profiles for current players to provide context to AI
                players = dict(session.players or {})
                players_rich_data = {}
                for pid, pdata in players.items():
                    players_rich_data[pid] = pdata.copy()
                    if pdata.get("truth_analysis_enabled"):
                        players_rich_data[pid]["profile_summary"] = await get_user_profile_summary(self.db, pid)

                analysis_results = await analyze_gameplay(session.game_slug, session.history, players_rich_data)
                
                if analysis_results:
                    current_analysis = dict(session.analysis or {})
                    # Update scores/stats based on analysis
                    for pid, data in analysis_results.items():
                        # Update global session analysis
                        current_analysis[pid] = data
                        
                        # Also update player score in the players dict for easy UI access
                        if pid in players:
                            players[pid]["score"] = (players[pid].get("score", 0) + data.get("insight_points_awarded", 0))
                            # Cache the latest fun commentary
                            players[pid]["last_commentary"] = data.get("fun_commentary")
                            players[pid]["truth_mismatch"] = data.get("truth_mismatch_detected", False)
                            
                    session.players = players
                    flag_modified(session, "players")
                    session.analysis = current_analysis
                    flag_modified(session, "analysis")
            except Exception as e:
                print(f"AI Analysis failed: {e}")
            
        await self.db.commit()
        await self.db.refresh(session)
        return session
