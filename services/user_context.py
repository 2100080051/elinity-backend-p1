from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.user import Tenant

async def get_user_context_string(db: AsyncSession, user_id: str) -> str:
    """
    Fetches comprehensive user profile data and returns a formatted context string
    for AI system prompts.
    """
    try:
        # Load user with deep profile relations
        # We use selectinload for async compatibility with relationships
        query = select(Tenant).where(Tenant.id == user_id).options(
            selectinload(Tenant.personal_info),
            selectinload(Tenant.big_five_traits),
            selectinload(Tenant.values_beliefs_and_goals),
            selectinload(Tenant.lifestyle),
            selectinload(Tenant.interests_and_hobbies)
        )
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return "User Context: Unknown User (Guest)"

        # Build Context String
        parts = []
        
        # 1. Identity
        if user.personal_info:
            name = f"{user.personal_info.first_name} {user.personal_info.last_name}".strip()
            parts.append(f"Name: {name}")
            if user.personal_info.age:
                parts.append(f"Age: {user.personal_info.age}")
            if user.personal_info.occupation:
                parts.append(f"Occupation: {user.personal_info.occupation}")
        
        # 2. Personality
        if user.big_five_traits:
            # traits are stored as JSON/Float, assuming 0-1 or 1-5 scale. We just dump raw for now.
            parts.append("Personality Traits (Big 5):")
            parts.append(f"- Openness: {user.big_five_traits.openness}")
            parts.append(f"- Conscientiousness: {user.big_five_traits.conscientiousness}")
            parts.append(f"- Extraversion: {user.big_five_traits.extraversion}")
            parts.append(f"- Agreeableness: {user.big_five_traits.agreeableness}")
            parts.append(f"- Neuroticism: {user.big_five_traits.neuroticism}")

        # 3. Values & Goals
        if user.values_beliefs_and_goals:
            if user.values_beliefs_and_goals.values:
                 parts.append(f"Core Values: {', '.join(map(str, user.values_beliefs_and_goals.values))}")
            if user.values_beliefs_and_goals.personal_goals:
                 parts.append(f"Personal Goals: {', '.join(map(str, user.values_beliefs_and_goals.personal_goals))}")

        # 4. Interests
        if user.interests_and_hobbies:
             if user.interests_and_hobbies.interests:
                 parts.append(f"Interests: {', '.join(map(str, user.interests_and_hobbies.interests))}")

        context_str = "\n".join(parts)
        return f"USER DEEP PROFILE CONTEXT:\n{context_str}\n\nINSTRUCTION: Adapt your coaching style, tone, and examples to fit this user's profile."

    except Exception as e:
        print(f"Error generating user context: {e}")
        return "User Context: Error fetching profile."
