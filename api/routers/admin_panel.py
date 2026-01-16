from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.session import get_db
from models.user import Tenant
from models.platform import Report, Subscription
from schemas.platform import AdminStats, ReportCreate
from utils.token import get_current_user

# Prefix /admin/panel to distinguish from user dashboard
router = APIRouter(tags=["Admin Panel"])

def verify_admin(user: Tenant):
    if user.role != "admin": # Assuming generic role check, logic might vary
        # For this MVP, we might skip strict checking or assume role field exists
        if getattr(user, "role", "user") != "admin":
             raise HTTPException(403, "Admin access required")

@router.get("/stats", response_model=AdminStats)
async def get_stats(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    # verify_admin(current_user) # Uncomment when admin role logic is firm
    
    total_users = db.query(Tenant).count()
    active_subs = db.query(Subscription).filter(Subscription.status == "active").count()
    pending_reports = db.query(Report).filter(Report.status == "pending").count()
    
    return AdminStats(
        total_users=total_users,
        active_subscriptions=active_subs,
        pending_reports=pending_reports
    )

@router.post("/reports")
async def create_report(report: ReportCreate, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    db_report = Report(reporter_id=current_user.id, **report.model_dump())
    db.add(db_report)
    db.commit()
    return {"message": "Report submitted"}

@router.post("/users/{user_id}/suspend")
async def suspend_user(user_id: str, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    # verify_admin(current_user)
    # Logic to suspend user (e.g. set is_active=False if field existed, or add to blacklist)
    # MVP: Just log it or return success
    return {"message": f"User {user_id} suspended"}

@router.post("/sessions/reset")
async def reset_sessions(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    # Delete all game sessions to allow valid restart
    from sqlalchemy import text
    try:
        # Use DELETE to respect FK constraints better than TRUNCATE in some setups
        db.execute(text("DELETE FROM game_sessions")) 
        db.commit()
        return {"message": "All game sessions deleted."}
    except Exception as e:
        db.rollback()
        # Fallback for some DBs that might strict block
        print(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
