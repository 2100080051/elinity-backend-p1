from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from database.session import Base
import uuid

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Game Identification
    game_slug = Column(String, nullable=False, index=True) # e.g. "ai-adventure-dungeon"
    game_mode = Column(String, nullable=True) # e.g. "co-op", "versus"
    
    # Room Details
    room_code = Column(String(10), unique=True, index=True, nullable=True) # Short code for sharing
    status = Column(String, default="lobby") # lobby, active, finished
    max_players = Column(Integer, default=5)
    
    # Participants
    host_user_id = Column(String, nullable=True) 
    players = Column(JSON, default=dict) # {"user_id": {"name": "...", "is_ready": bool, "avatar": "..."}}
    
    # State & Analysis
    state = Column(JSON, default=dict) 
    analysis = Column(JSON, default=dict) # AI psycho-analysis per player
    history = Column(JSON, default=list) 
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
