from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import Tenant, PersonalInfo, BigFiveTraits, Psychology
from sqlalchemy.orm import selectinload

async def get_user_profile_summary(db: AsyncSession, user_id: str):
    """Fetches a high-level summary of the user's psychological and personal profile."""
    # We use selectinload to get detailed traits if they exist
    result = await db.execute(
        select(Tenant)
        .options(
            selectinload(Tenant.personal_info),
            selectinload(Tenant.big_five_traits),
            selectinload(Tenant.psychology)
        )
        .where(Tenant.id == user_id)
    )
    user = result.scalars().first()
    if not user: return "Guest Traveller"

    summary = []
    if user.personal_info:
        summary.append(f"Occupation: {user.personal_info.occupation}")
        summary.append(f"Gender: {user.personal_info.gender}")
    
    if user.big_five_traits:
        traits = user.big_five_traits
        summary.append(f"Traits: Openness={traits.openness}, Extraversion={traits.extraversion}, Conscientiousness={traits.conscientiousness}")
    
    if user.psychology:
        summary.append(f"Attachment Style: {user.psychology.attachment_style}")
        summary.append(f"Cognitive Style: {user.psychology.cognitive_style}")

    return " | ".join(summary) if summary else "Unknown Persona"
