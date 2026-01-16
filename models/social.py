from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Boolean
from database.session import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, default=gen_uuid)
    host_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    attendees = Column(JSON, default=[])  # List of user IDs
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class SocialPost(Base):
    __tablename__ = "social_posts"
    id = Column(String, primary_key=True, default=gen_uuid)
    author_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    content = Column(String, nullable=True)
    media_urls = Column(JSON, default=[]) # List of image/video URLs
    likes = Column(JSON, default=[]) # List of user IDs who liked
    comments = Column(JSON, default=[]) # List of dicts: {user_id, content, timestamp}
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class SocialInteraction(Base):
    """Tracks generic interactions like Likes, Stars, etc."""
    __tablename__ = "social_interactions"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    target_id = Column(String, nullable=False) # ID of Post, Event, or User
    target_type = Column(String, nullable=False) # 'post', 'event', 'user'
    interaction_type = Column(String, nullable=False) # 'like', 'star', 'bookmark'
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
