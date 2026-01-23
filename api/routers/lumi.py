from api.routers._profile_helper import get_user_profile_summary
from elinity_ai.modes.prompts import SYSTEM_PROMPT_LUMI
from database.session import get_db, Session
from utils.token import get_current_user
from models.user import Tenant
from fastapi import Depends, APIRouter
from services.ai_service import AIService

router = APIRouter(tags=["Lumi Core"])

@router.post("/chat/")
async def lumi_endpoint(query: str, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Lumi: Your core AI companion for deep connection and personal flourishing."""
    ai = AIService()
    
    # Get high-level user context for a personalized 'thinking partner' experience
    user_context = await get_user_profile_summary(db, current_user.id)
    
    # Lumi System Prompt with user context
    full_system_content = f"{SYSTEM_PROMPT_LUMI}\n\nUSER CONTEXT: {user_context}"
    
    resp = await ai.chat([
        {"role": "system", "content": full_system_content},
        {"role": "user", "content": query}
    ])
    return {"LumiAI": resp}
