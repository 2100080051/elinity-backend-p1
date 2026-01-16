from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Float
from database.session import Base

def gen_uuid():
    return str(uuid.uuid4())

class Connection(Base):
    """
    Tracks the lifecycle of a connection between two users across different modes.
    Implements the P1 flow: Recommendation -> One-way Accept -> Two-way Match -> Personal Circle.
    """
    __tablename__ = "connections"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    
    # Participants
    # User A is typically the one who received the recommendation first
    user_a_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_b_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    # Metadata
    mode = Column(String, nullable=False) # 'romantic', 'social', 'professional'
    score = Column(Float, default=0.0)
    
    # Status Machine:
    # 'suggested'  -> Sent to User A as daily rec (Hidden from B)
    # 'pending_b'  -> User A accepted, waiting for User B to see/accept
    # 'matched'    -> Both accepted (Chat Open, Icebreakers)
    # 'personal'   -> Moved to Personal Circle (Search disabled if Romantic)
    # 'declined'   -> User A or B declined (Feedback stored)
    # 'archived'   -> User A archived it for later
    status = Column(String, default="suggested")
    
    # Interaction Data
    ai_icebreaker = Column(String, nullable=True) # Generated on match
    
    # Feedback structure: {"declined_by": "user_id", "reason": "text", "feedback": "text"}
    feedback = Column(JSON, default={}) 
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
