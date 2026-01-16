from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class SubscriptionResponse(BaseModel):
    tier: str
    status: str
    expiry_date: Optional[datetime]
    class Config:
        from_attributes = True

class ReferralCreate(BaseModel):
    referee_email: str

class ReferralResponse(BaseModel):
    code: str
    points_earned: int
    count: int
    class Config:
        from_attributes = True

class ReportCreate(BaseModel):
    reported_id: str
    reason: str
    description: Optional[str]

class AdminStats(BaseModel):
    total_users: int
    active_subscriptions: int
    pending_reports: int
