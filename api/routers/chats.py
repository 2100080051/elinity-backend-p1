from fastapi import APIRouter, Depends, HTTPException, status
from models.chat import Chat, Group, GroupMember
from database.session import get_db, Session
from utils.token import get_current_user
from models.user import Tenant
from schemas.chat import ChatSchema, ChatCreateSchema
from services.ai_service import AIService
import json
from sqlalchemy.orm import joinedload

router = APIRouter()
ai_service = AIService()

# ---------------------------
# Get all chats for user
# ---------------------------
@router.get("/", tags=["Chats"])
async def get_chats(
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Chat).filter(Chat.sender == current_user.id).all()


# ---------------------------
# Create new chat
# ---------------------------
@router.post("/", tags=["Chats"], response_model=ChatSchema)
async def create_chat(
    chat: ChatCreateSchema,   # ✅ use create schema
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # sender is always current_user
    chat_obj = Chat(sender=current_user.id, **chat.model_dump())
    db.add(chat_obj)
    db.commit()
    db.refresh(chat_obj)
    return chat_obj


@router.post("/direct/{target_id}", tags=["Chats"]) 
async def send_direct_message(target_id: str, payload: dict, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Send a direct message to another user. Automatically creates a private group (dm_{a}_{b}) and stores messages."""
    message = payload.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="message is required")
    if target_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")

    # Ensure target exists
    target = db.query(Tenant).filter(Tenant.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    # Create deterministic DM group name
    ids = sorted([current_user.id, target_id])
    group_name = f"dm_{ids[0]}_{ids[1]}"

    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        group = Group(name=group_name, tenant=current_user.id, description=f"Direct messages between {ids[0]} and {ids[1]}", type='users_ai')
        db.add(group); db.commit(); db.refresh(group)
        # add members
        gm1 = GroupMember(group=group.id, tenant=current_user.id)
        gm2 = GroupMember(group=group.id, tenant=target_id)
        db.add_all([gm1, gm2]); db.commit()

    asset_id = payload.get("asset_url") or payload.get("asset_id")

    # store chat message in group
    chat_obj = Chat(sender=current_user.id, receiver=target_id, group=group.id, message=message, asset_url=asset_id)
    db.add(chat_obj); db.commit(); db.refresh(chat_obj)

    return {"status": "ok", "chat_id": chat_obj.id, "group_id": group.id}


@router.post("/{group_id}/analysis", tags=["Chats"])
async def analyze_group_chat(group_id: str, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Run AI analysis on a group's recent conversation: suggestions, tone, quick feedback."""
    # Load recent messages
    chats = db.query(Chat).filter(Chat.group == group_id).order_by(Chat.created_at.asc()).all()
    if not chats:
        raise HTTPException(status_code=404, detail="No chats found for group")

    transcript = "\n".join([f"{c.sender}:{c.message}" for c in chats[-50:]])
    prompt = (
        "You are a helpful assistant. Analyze the following conversation and provide:\n"
        "1) A short summary (1-2 sentences)\n"
        "2) Tone detection (e.g., friendly, annoyed, neutral)\n"
        "3) 3 short suggestions to improve the conversation or next steps\n"
        "Return a JSON object with keys: summary, tone, suggestions.\n\nConversation:\n" + transcript
    )

    try:
        from services.ai_service import AIService
        ai_service = AIService()
        # ai_service.chat() is async, so await it directly
        resp_text = await ai_service.chat([{"role": "system", "content": prompt}])
    except Exception as e:
        # Log the error for debugging, but return a structured response
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error during chat analysis: {str(e)}")
        resp_text = "(ai error)"

    # try parse JSON
    parsed = None
    try:
        parsed = json.loads(resp_text)
    except Exception:
        parsed = {"summary": resp_text, "tone": None, "suggestions": []}

    return {"analysis": parsed}


@router.post("/icebreaker", tags=["Chats"])
async def get_icebreaker(mode: str = "universal"):
    """Get a random icebreaker prompt based on mode (universal, romantic, leisure, work)."""
    from elinity_ai.modes.prompts import (
        ICEBREAKER_TWO_TRUTHS, ICEBREAKER_SWIPE_SHARE, ICEBREAKER_DATE_DEBATE
    )
    # Mapping modes to specific icebreakers (MVP random pick)
    import random
    options = [ICEBREAKER_TWO_TRUTHS, ICEBREAKER_SWIPE_SHARE, ICEBREAKER_DATE_DEBATE]
    return {"icebreaker": random.choice(options)}

@router.post("/vibe-check", tags=["Chats"])
async def trigger_vibe_check(type: str = "personality"):
    """Get a vibe check prompt for voice/video response."""
    prompts = {
        "personality": "Tell me the story behind your favorite scar, tattoo, or keepsake.",
        "playful": "Tell me a 20-second story using the words: banana, stars, and betrayal.",
        "values": "What’s something you deeply value that others often overlook?",
        "fun": "What's a weird skill or fact you know that nobody expects?"
    }
    return {"prompt": prompts.get(type, prompts["personality"])}

# ---------------------------
# Get single chat by ID
# ---------------------------
@router.get("/{chat_id}", tags=["Chats"], response_model=ChatSchema)
async def get_chat(
    chat_id: str,  # UUID
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat_obj = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat_obj
