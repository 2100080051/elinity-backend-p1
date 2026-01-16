from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel

class GoalRitualCreate(BaseModel):
    title: str
    description: Optional[str] = None
    frequency: str = "daily"

class GoalRitualResponse(GoalRitualCreate):
    id: str
    streak_count: int
    history: List[str] = []
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class NudgeResponse(BaseModel):
    id: str
    type: str
    content: str
    scheduled_for: Optional[datetime]
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

class MoodboardCreate(BaseModel):
    title: str
    type: str = "personal"
    items: List[Dict[str, Any]] = []

class MoodboardResponse(MoodboardCreate):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True

class PhotoJournalCreate(BaseModel):
    image_url: str
    caption: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = []

class PhotoJournalResponse(PhotoJournalCreate):
    id: str
    date: datetime
    class Config:
        from_attributes = True

class QuizCreate(BaseModel):
    title: str
    description: Optional[str]
    questions: List[Dict[str, Any]]
    is_system: bool = False

class QuizResponse(QuizCreate):
    id: str
    created_by: Optional[str]
    class Config:
        from_attributes = True
