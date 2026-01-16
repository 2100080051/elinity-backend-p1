from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Boolean, Float
from database.session import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class AdminLog(Base):
    """Audit logs for admin actions."""
    __tablename__ = "admin_logs"
    id = Column(String, primary_key=True, default=gen_uuid)
    admin_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    action = Column(String, nullable=False) # 'ban_user', 'delete_post'
    target = Column(String, nullable=True) # ID of the target object
    details = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    __table_args__ = {'extend_existing': True}

class Report(Base):
    """User reports against content or other users."""
    __tablename__ = "reports"
    id = Column(String, primary_key=True, default=gen_uuid)
    reporter_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    reported_id = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, resolved, dismissed
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    __table_args__ = {'extend_existing': True}

class Subscription(Base):
    """User subscription status."""
    __tablename__ = "subscriptions"
    id = Column(String, primary_key=True, default=gen_uuid)
    tenant = Column(String, ForeignKey("tenants.id"), nullable=False)
    tier = Column(String, default="free") # free, premium, vip
    status = Column(String, default="active")
    expiry_date = Column(DateTime, nullable=True)
    provider_id = Column(String, nullable=True) # Stripe ID
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    __table_args__ = {'extend_existing': True}

class Referral(Base):
    """Referral tracking."""
    __tablename__ = "referrals"
    id = Column(String, primary_key=True, default=gen_uuid)
    referrer_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    referee_id = Column(String, nullable=True) # Can be null if pending invitation
    code = Column(String, unique=True, nullable=False)
    status = Column(String, default="pending") # pending, completed
    points_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    __table_args__ = {'extend_existing': True}
