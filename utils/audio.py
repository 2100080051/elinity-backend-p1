import os
import uuid
import logging

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_AUDIO_DIR = os.path.join(BASE_DIR, 'static', 'onboarding_audio')
os.makedirs(STATIC_AUDIO_DIR, exist_ok=True)

logger = logging.getLogger(__name__)

def transcribe_audio(audio_path: str):
    """MOCK: Transcribe audio to text. Returns dummy text."""
    logger.info(f"MOCK: Transcribing audio file {audio_path}")
    return "This is a simulated transcription of the user's voice for testing purposes."

def text_to_speech(text: str) -> str:
    """MOCK: Convert text to speech. Creates a dummy file.
    Returns absolute path to the generated file.
    """
    if not text:
        raise ValueError("No text provided for TTS")

    filename = f"onb_{uuid.uuid4().hex}.mp3"
    out_path = os.path.join(STATIC_AUDIO_DIR, filename)

    # Create a dummy empty file or minimal valid MP3 header if needed
    # For now, just an empty text file with mp3 extension is enough for file existence check
    with open(out_path, 'w') as f:
        f.write("MOCK AUDIO CONTENT")
    
    logger.info(f"MOCK: Generated TTS audio at {out_path}")
    return out_path
