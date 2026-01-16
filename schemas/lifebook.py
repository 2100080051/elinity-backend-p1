from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional, Dict, Any

class LifebookBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    content: Dict[str, Any] = {}

class LifebookCreate(LifebookBase):
    pass

class LifebookResponse(LifebookBase):
    id: str
    tenant: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LifebookEntryBase(BaseModel):
    title: str
    content: str
    media_urls: List[str] = []

class LifebookEntryCreate(LifebookEntryBase):
    lifebook_id: str

class LifebookEntryResponse(LifebookEntryBase):
    id: str
    lifebook_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
