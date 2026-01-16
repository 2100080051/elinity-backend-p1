import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from utils.token import get_current_user
from models.user import Tenant
from schemas.multimodal import MultimodalSchema,MultimodalResponse
from database.session import get_async_db
from ._profile_helper import get_user_profile_summary

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/process/", tags=["Multimodal"], response_model=MultimodalResponse)
async def process(request: MultimodalSchema, current_user: Tenant = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)) -> dict:
    # Lazy Load to prevent Import/Init failures from breaking the whole router
    from elinity_ai.multimodal import ElinityMultimodal
    from elinity_ai.smart_journal import ElinitySmartJournal
    
    transcript = ElinityMultimodal()
    smart_journal = ElinitySmartJournal()
    
    try:
        try:
            # Attempt to process the URL using the multimodal client
            result = transcript.process(request.url)
        except Exception as inner_e:
            logger.warning(f"Multimodal processing failed (likely missing keys or invalid URL), falling back to stub: {inner_e}")
            # Fallback stub for demonstration/testing when external services aren't configured
            result = "This is a placeholder transcript. The audio processing service could not be reached or failed. (Original audio URL: " + request.url + ")"
        
        # TRUTH ANALYSIS: Fetch Profile
        user_profile = await get_user_profile_summary(db, current_user.id)

        insights = await smart_journal.generate_insights(result, user_profile=user_profile)
        # Ensure insights is not None
        if insights is None:
            insights = "Unable to generate insights at this time."
        return MultimodalResponse(url=request.url,text=result,insights=insights)
    except Exception as e:
        logger.error(f"Error processing multimodal: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
