from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.auth import RegisterRequest, RefreshRequest, LoginRequest, Token
from datetime import datetime, timezone  

from models.user import (
    Tenant,
    PersonalInfo,
    BigFiveTraits,
    MBTITraits,
    Psychology,
    InterestsAndHobbies,
    ValuesBeliefsAndGoals,
    Favorites,
    RelationshipPreferences,
    FriendshipPreferences,
    AspirationAndReflections,
    IdealCharacteristics,
    CollaborationPreferences,
    PersonalFreeForm,
    Intentions,
) 
from models.user import Tenant
from models.notifications import Notification
from utils.token import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_access_from_refresh,
    get_current_user
)
from fastapi.security import OAuth2PasswordRequestForm

# {
#   "email": "johndoe@elinity.com",
#   "phone": "9102472789",
#   "password": "E4DOJ309#ESF"
# }

router = APIRouter(tags=['Authentication'])


@router.post("/register", response_model=Token )
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not req.email and not req.phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone is required")
    key_filter = []
    if req.email:
        key_filter.append(Tenant.email == req.email)
    if req.phone:
        key_filter.append(Tenant.phone == req.phone)
    exists = db.query(Tenant).filter(*key_filter).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
    hashed = get_password_hash(req.password)
    tenant_obj = Tenant(
        email=req.email,
        phone=req.phone,
        password=hashed,
        last_login=None
    )
    db.add(tenant_obj)
    db.commit(); db.refresh(tenant_obj)
    # Initialize related profile records
    db.add_all([
        PersonalInfo(tenant=tenant_obj.id),
        BigFiveTraits(tenant=tenant_obj.id),
        MBTITraits(tenant=tenant_obj.id),
        Psychology(tenant=tenant_obj.id),
        InterestsAndHobbies(tenant=tenant_obj.id),
        ValuesBeliefsAndGoals(tenant=tenant_obj.id),
        Favorites(tenant=tenant_obj.id),
        RelationshipPreferences(tenant=tenant_obj.id),
        FriendshipPreferences(tenant=tenant_obj.id),
        CollaborationPreferences(tenant=tenant_obj.id),
        PersonalFreeForm(tenant=tenant_obj.id),
        Intentions(tenant=tenant_obj.id),
        AspirationAndReflections(tenant=tenant_obj.id),
        IdealCharacteristics(tenant=tenant_obj.id),
    ])
    db.commit()
    access_token = create_access_token({"sub": tenant_obj.id, "role": tenant_obj.role})
    refresh_token = create_refresh_token({"sub": tenant_obj.id, "role": tenant_obj.role})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/login", response_model=Token )
async def login(req: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate via JSON email/phone & password"""
    if req.email:
        user = db.query(Tenant).filter(Tenant.email == req.email).first()
    elif req.phone:
        user = db.query(Tenant).filter(Tenant.phone == req.phone).first()
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone required")
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    user.last_login = datetime.now(timezone.utc)
    db.commit(); db.refresh(user)
    access_token = create_access_token({"sub": user.id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id, "role": user.role})

    # Auto-detect incomplete profile: if key profile sections missing, create notification
    try:
        pinfo = user.personal_info
        incomplete = False
        if not pinfo:
            incomplete = True
        else:
            # If age or location or profile_pictures empty, mark incomplete
            if not pinfo.age or not pinfo.first_name or not pinfo.location:
                incomplete = True
        if incomplete:
            note = Notification(tenant=user.id, title="Please complete your profile", message="We noticed some profile sections are incomplete. Please complete your profile to get better recommendations.")
            db.add(note); db.commit()
    except Exception:
        # non-fatal
        pass
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    """Authenticate via form-data (for Swagger OAuth2)"""
    username = form_data.username
    password = form_data.password
    if "@" in username:
        user = db.query(Tenant).filter(Tenant.email == username).first()
    else:
        user = db.query(Tenant).filter(Tenant.phone == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    user.last_login = datetime.now(timezone.utc)
    db.commit(); db.refresh(user)
    access_token = create_access_token({"sub": user.id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id, "role": user.role})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post('/refresh', response_model=Token)
async def refresh_token_endpoint(refresh_req: RefreshRequest, db: Session = Depends(get_db)):
    token = refresh_req.refresh_token
    # Treat missing or literal "null" as invalid
    if not token or token.strip().lower() == "null":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is required")
    try:
        access_token = create_access_from_refresh(token)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return Token(access_token=access_token, refresh_token=token, token_type='bearer')


@router.post('/create_service_key')
async def create_service_key(name: str = None, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a long-lived service API key for internal use.

    Admin-only. Returns the plain API key exactly once.
    """
    # Resolve current user and enforce admin role
    user = current_user
    if not user or not hasattr(user, 'role') or user.role.lower() != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin privileges required')

    # Lazy import to avoid circulars
    from models.service_key import ServiceKey
    from utils.token import get_password_hash
    import secrets

    plain_key = secrets.token_urlsafe(48)
    hashed = get_password_hash(plain_key)

    sk = ServiceKey(name=name or 'auto-generated', key_hash=hashed, created_by=user.id)
    db.add(sk)
    db.commit()
    db.refresh(sk)

    return {"api_key": plain_key, "id": sk.id}