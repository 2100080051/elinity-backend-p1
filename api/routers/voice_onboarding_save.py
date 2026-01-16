from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any
import logging
import json

from database.session import get_db, Session
from utils.token import get_current_user
from models.user import Tenant
from models.chat import Chat, Group
from elinity_ai.onboarding_conversation import ElinityOnboardingConversation
from schemas.profile_schema import GeneratedProfileSchema
from utils.profile_mapper import persist_profile

router = APIRouter(prefix="", tags=["Voice Onboarding Save"])

logger = logging.getLogger("voice_onboarding_save")


def _extract_json_from_text(text: str):
    # handle code fences
    try:
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            json_str = text.strip()
        return json.loads(json_str)
    except Exception as e:
        logger.exception("Failed to parse JSON from analysis response")
        raise


@router.post('/voice/finalize')
async def finalize_profile(current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate structured profile JSON from the onboarding conversation history. Does NOT persist to DB."""
    group_name = f"onboarding_{current_user.id}"
    group = db.query(Group).filter(Group.name == group_name).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No onboarding session found for user")

    chats = db.query(Chat).filter(Chat.group == group.id).all()
    if not chats:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No conversation history found")

    # Build conversation text
    conversation_text = "\n\n".join([f"{('user' if c.sender == current_user.id else 'assistant')}: {c.message}" for c in chats])

    # Build strict analysis prompt
    analysis_prompt = (
        "Based on the conversation below, extract the user's profile as JSON following this schema:"
    )
    analysis_prompt += "\nPlease return only valid JSON matching the fields: personal_info, interests_and_hobbies, values_beliefs_and_goals, relationship_preferences.\n"
    analysis_prompt += f"\nConversation to analyze:\n{conversation_text}"

    try:
        model = ElinityOnboardingConversation()
        analysis_chat = model.model.start_chat()
        analysis_response = analysis_chat.send_message({"parts": [{"text": analysis_prompt}]})
        response_text = analysis_response.text
        parsed = _extract_json_from_text(response_text)

        # Validate with pydantic schema (allows partials)
        profile = GeneratedProfileSchema(**parsed)
        return profile.dict()
    except Exception as e:
        logger.exception("Profile generation failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/voice/confirm-save')
async def confirm_and_save_profile(profile: Any, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Validate and persist generated profile into user-related tables. Returns saved entities."""
    try:
        # Validate schema; allow extra fields in 'other'
        prof = GeneratedProfileSchema(**profile)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid profile format: {str(e)}")

    try:
        results = persist_profile(db, current_user.id, prof.dict())
        return {"status": "saved", "details": "Profile persisted", "results": {k: getattr(v, 'id', None) for k, v in results.items()}}
    except Exception as e:
        logger.exception("Failed to save profile")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
