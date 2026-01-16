from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Boolean
from database.session import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class GoalRitual(Base):
    """Tracks habits, rituals, and streaks."""
    __tablename__ = "rituals"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    frequency = Column(String, default="daily") # daily, weekly
    streak_count = Column(Integer, default=0)
    history = Column(JSON, default=[]) # List of dates when completed
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    __table_args__ = {'extend_existing': True}

class Nudge(Base):
    """AI Reminders and Nudges."""
    __tablename__ = "nudges"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    type = Column(String, nullable=False) # 'reminder', 'suggestion', 'alert'
    content = Column(String, nullable=False)
    scheduled_for = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class Moodboard(Base):
    """Visual moodboards for relationships or personal life."""
    __tablename__ = "moodboards"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, default="personal") # 'personal', 'relationship'
    items = Column(JSON, default=[]) # List of {type: 'image'|'text', url: '', content: ''}
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class PhotoJournal(Base):
    """Photo-based journaling."""
    __tablename__ = "photo_journals"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    image_url = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    location = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.now(timezone.utc))
    tags = Column(JSON, default=[]) # e.g. ['travel', 'food']

class Quiz(Base):
    """Interactive quizzes."""
    __tablename__ = "quizzes"
    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    questions = Column(JSON, default=[]) # List of Question objects
    created_by = Column(String, ForeignKey("tenants.id"), nullable=True) # Null for system quizzes
    is_system = Column(Boolean, default=False)

class QuizResult(Base):
    """User results for quizzes."""
    __tablename__ = "quiz_results"
    id = Column(String, primary_key=True, default=gen_uuid)
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    score = Column(Integer, default=0)
    answers = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
