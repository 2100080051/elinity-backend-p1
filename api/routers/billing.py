from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from models.user import Tenant
from models.platform import Subscription, Referral
from schemas.platform import SubscriptionResponse, ReferralResponse
from utils.token import get_current_user
import uuid
from typing import List, Dict

router = APIRouter(tags=["Billing"])

PLANS = [
    {
        "id": "free",
        "name": "Elinity Basic",
        "price": 0.00,
        "features": ["Basic Journaling", "Community Feed", "Daily Rituals"]
    },
    {
        "id": "premium",
        "name": "Elinity Premium",
        "price": 9.99,
        "features": ["Voice Journaling", "Unlimited AI Chat", "Advanced Relationship Dashboard", "Private Mode"]
    },
    {
        "id": "family",
        "name": "Elinity Family",
        "price": 19.99,
        "features": ["All Premium Features", "Up to 5 Family Members", "Shared Calendars", "Family Moodboard"]
    }
]

@router.get("/plans", response_model=List[Dict])
async def list_plans():
    """List available subscription plans."""
    return PLANS

@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    sub = db.query(Subscription).filter(Subscription.tenant == current_user.id).first()
    if not sub:
        # Create default free sub
        sub = Subscription(tenant=current_user.id, tier="free")
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub

@router.post("/subscription/upgrade")
async def upgrade_subscription(tier: str, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Integration stub for upgrading description."""
    valid_tiers = [p['id'] for p in PLANS]
    if tier not in valid_tiers:
        return {"error": "Invalid tier"}
        
    sub = db.query(Subscription).filter(Subscription.tenant == current_user.id).first()
    if not sub:
        sub = Subscription(tenant=current_user.id)
        db.add(sub)
    
    sub.tier = tier
    sub.status = "active"
    db.commit()
    return {"message": f"Upgraded to {tier}"}

@router.get("/referrals", response_model=ReferralResponse)
async def get_referrals(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    # Simple logic: count referrals
    count = db.query(Referral).filter(Referral.referrer_id == current_user.id, Referral.status == "completed").count()
    
    # Get or create code
    my_ref = db.query(Referral).filter(Referral.referrer_id == current_user.id, Referral.referee_id == None).first()
    if not my_ref:
        code = str(uuid.uuid4())[:8]
        # Store as a template referral for the code
        # Actually, code should be on User model usually, but here we can just return a generated one for MVP
        code = f"REF-{current_user.id[:4]}"
    else:
        code = my_ref.code
        
    return ReferralResponse(code=code, points_earned=count*10, count=count)
