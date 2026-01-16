from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Text
from database.session import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class Lifebook(Base):
    """Stores a user's Lifebook chapters and entries."""
    __tablename__ = "lifebooks"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False) # e.g., 'Health', 'Wealth', 'Relationships', 'Career', 'Spiritual'
    content = Column(JSON, default={}) # Detailed goals, visions, and strategies
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class LifebookEntry(Base):
    """Individual reflections or milestones within a Lifebook category."""
    __tablename__ = "lifebook_entries"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    lifebook_id = Column(String, ForeignKey("lifebooks.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
