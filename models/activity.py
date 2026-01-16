from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Text
from database.session import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class UserActivity(Base):
    """
    Centralized log of all user activities for Deep Profiling and Analytics.
    Tracks: Skill sessions, Game plays, Profile updates, etc.
    """
    __tablename__ = "user_activities"

    id = Column(String, primary_key=True, default=gen_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    # Category of activity: "skill", "game", "profile", "social", "system"
    activity_type = Column(String, nullable=False)
    
    # Specific target identifier (e.g. skill_id="1", game_name="comic-creator")
    target_id = Column(String, nullable=True)
    
    # Detailed metadata (e.g. {"session_number": 1, "score": 100, "changes": ["email"]})
    details = Column(JSON, default={})
    
    timestamp = Column(DateTime, default=datetime.utcnow)
