from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class QuestionCardQuery(BaseModel):
    count: int = 25

class QuestionCardAnswerCreate(BaseModel):
    card_content: str
    answer: str

class QuestionCardAnswerResponse(BaseModel):
    id: uuid.UUID
    card_content: str
    answer: str
    created_at: datetime
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True

from typing import List, Literal, Optional

class QuestionCard(BaseModel):
    """Structured question/prompt card model"""
    text: str
    category: Optional[str] = "General"
    color: Optional[str] = "#FFFFFF"
    tags: List[str] = []
    difficulty_level: Optional[Literal["easy", "medium", "hard"]] = "easy"
