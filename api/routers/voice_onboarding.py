from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import FileResponse
import logging
import os
import uuid
from sqlalchemy import exists

from models.chat import Group, Chat
from database.session import get_db, Session
from utils.token import get_current_user
from models.user import Tenant
from models.user import PersonalInfo, InterestsAndHobbies, Favorites, RelationshipPreferences

from elinity_ai.multimodal import ElinityMultimodal
from elinity_ai.onboarding_conversation import ElinityOnboardingConversation

from utils import audio as audio_utils

router = APIRouter(prefix="", tags=["Voice Onboarding"])

logger = logging.getLogger("voice_onboarding")

# mul_model = ElinityMultimodal() # Moved inside functions


@router.post('/voice/start')
async def start_voice_onboarding(current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create onboarding group and return welcome message + tts audio filename."""
    model = ElinityOnboardingConversation()

    group_name = f"onboarding_{current_user.id}"

    group = db.query(Group).filter(Group.name == group_name).first()

    # Create group if missing
    if not group:
        group = Group(name=group_name, tenant=current_user.id, description=f"Onboarding Group for {current_user.id}", type='user_ai')
        db.add(group)
        db.commit(); db.refresh(group)

    chat_exists = db.query(exists().where(Chat.group == group.id)).scalar()
    if chat_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already have chat started. Please continue the chat.")

    # create first assistant chat with welcome message
    chat = Chat(group=group.id, message=model.welcome_message, receiver=current_user.id)
    db.add(chat)
    db.commit(); db.refresh(chat)

    # generate tts audio and return filename
    try:
        audio_path = audio_utils.text_to_speech(model.welcome_message)
        audio_filename = os.path.basename(audio_path)
    except Exception as e:
        logger.exception("TTS generation failed")
        audio_filename = None

    return {
        "tenant_id": current_user.id,
        "message": model.welcome_message,
        "audio_filename": audio_filename,
    }


@router.put('/voice/continue')
async def continue_voice_onboarding(file: UploadFile | None = File(None), asset_url: str | None = None, text: str | None = None, current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Continue onboarding by accepting an audio upload, or text, or asset URL. Returns assistant message and tts filename."""
    group_name = f"onboarding_{current_user.id}"

    group_exists = db.query(exists().where(Group.name == group_name)).scalar()
    if not group_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please start a chat before continuing.")

    group = db.query(Group).filter(Group.name == group_name).first()
    chat_exists = db.query(exists().where(Chat.group == group.id)).scalar()
    if not chat_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please start a chat before continuing.")

    # Determine prompt
    prompt = None
    user_text = None

    # If asset_url provided, prefer multimodal processing (existing behavior)
    if asset_url:
        try:
            prompt = ElinityMultimodal().process(asset_url)
            user_text = prompt
        except Exception:
            prompt = None

    # If direct text provided
    if not prompt and text:
        prompt = text
        user_text = text

    # If audio file provided, save and transcribe
    if not prompt and file is not None:
        try:
            # save to temp file
            suffix = os.path.splitext(file.filename)[1] or '.wav'
            tmp_name = f"{uuid.uuid4().hex}{suffix}"
            tmp_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'tmp')
            os.makedirs(tmp_dir, exist_ok=True)
            tmp_path = os.path.join(tmp_dir, tmp_name)
            with open(tmp_path, 'wb') as f:
                f.write(await file.read())

            user_text = audio_utils.transcribe_audio(tmp_path)
            prompt = user_text
        except Exception as e:
            logger.exception("Audio transcription failed")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Audio transcription failed: {str(e)}")

    if not prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No input provided. Provide audio file, text, or asset_url.")

    # Build conversation history from DB
    chats = db.query(Chat).filter(Chat.group == group.id).all()
    conversation_history = [
        # keep the same role mapping as other endpoints
        ("user" if c.sender == current_user.id else "assistant", c.message)
        for c in chats
    ]

    model = ElinityOnboardingConversation(conversation_history=[ ])

    # get next prompt from the model
    try:
        next_prompt = model.get_next_prompt(prompt)
    except Exception as e:
        logger.exception("Model failed to produce next prompt")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate assistant response")

    # store user and assistant chats
    try:
        chat_objs = [
            Chat(group=group.id, sender=current_user.id, message=user_text or (text or '' )),
            Chat(group=group.id, message=next_prompt, receiver=current_user.id)
        ]
        db.add_all(chat_objs)
        db.commit()
    except Exception:
        logger.exception("Saving chats failed")

    # If the user provided textual profile information, attempt to extract and persist
    if user_text:
        try:
            profile = None
            if hasattr(model, 'extract_profile_from_text'):
                profile = model.extract_profile_from_text(user_text)
            # profile expected to be dict with age, interests, hobbies, preferences, favorites
            if profile and isinstance(profile, dict):
                # Update PersonalInfo age if provided
                try:
                    pinfo = db.query(PersonalInfo).filter(PersonalInfo.tenant == current_user.id).first()
                    if not pinfo:
                        pinfo = PersonalInfo(tenant=current_user.id)
                        db.add(pinfo); db.commit(); db.refresh(pinfo)
                    if profile.get('age'):
                        pinfo.age = profile.get('age')
                    if profile.get('location'):
                        pinfo.location = profile.get('location')
                    db.add(pinfo); db.commit()
                except Exception:
                    pass

                try:
                    ih = db.query(InterestsAndHobbies).filter(InterestsAndHobbies.tenant == current_user.id).first()
                    if not ih:
                        ih = InterestsAndHobbies(tenant=current_user.id)
                        db.add(ih); db.commit(); db.refresh(ih)
                    if profile.get('interests'):
                        ih.interests = profile.get('interests')
                    if profile.get('hobbies'):
                        ih.hobbies = profile.get('hobbies')
                    db.add(ih); db.commit()
                except Exception:
                    pass

                try:
                    fav = db.query(Favorites).filter(Favorites.tenant == current_user.id).first()
                    if not fav:
                        fav = Favorites(tenant=current_user.id)
                        db.add(fav); db.commit(); db.refresh(fav)
                    if profile.get('favorites'):
                        # best-effort mapping
                        fav.music = profile.get('favorites') if isinstance(profile.get('favorites'), list) else fav.music
                    db.add(fav); db.commit()
                except Exception:
                    pass
        except Exception:
            logger.exception("Profile extraction failed")

    # generate tts for assistant response
    try:
        audio_path = audio_utils.text_to_speech(next_prompt)
        audio_filename = os.path.basename(audio_path)
    except Exception:
        logger.exception("TTS generation failed")
        audio_filename = None

    return {
        "tenant_id": current_user.id,
        "user_text": user_text,
        "message": next_prompt,
        "audio_filename": audio_filename,
    }


@router.get('/voice/audio/{filename}')
async def get_voice_audio(filename: str):
    """Serve generated onboarding audio files."""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    static_dir = os.path.abspath(os.path.join(base_dir, '..', 'static', 'onboarding_audio'))
    file_path = os.path.join(static_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")
    return FileResponse(path=file_path, media_type='audio/mpeg', filename=filename)
