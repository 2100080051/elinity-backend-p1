from services.ai_service import AIService, DEFAULT_MODEL
import os
from dotenv import load_dotenv

from elinity_ai.modes.prompts import (
    SYSTEM_PROMPT_MATCH_ROMANTIC, SYSTEM_PROMPT_MATCH_FRIENDSHIP, SYSTEM_PROMPT_MATCH_WORK
)

load_dotenv()

class ElinityInsights:
    def __init__(self, llm_model: str = None, langsmith_api_key: str = None):
        # We rely purely on AIService (OpenRouter) now
        pass

    def generate_insight(self, query, user_id, user_name, score, user_interests, match_type="general"):
        """Generate an AI insight using AIService (lightweight)."""
        
        system_prompt = "You are an insightful AI relationship expert."
        
        if "romantic" in query.lower() or match_type == "romantic":
            system_prompt = SYSTEM_PROMPT_MATCH_ROMANTIC
        elif "friend" in query.lower() or match_type == "friendship":
            system_prompt = SYSTEM_PROMPT_MATCH_FRIENDSHIP
        elif "work" in query.lower() or "collab" in query.lower() or match_type == "work":
            system_prompt = SYSTEM_PROMPT_MATCH_WORK

        formatted_prompt = (
            f"Generate a deep AI insight for candidate {user_name} (id={user_id}) with match score {score:.2f}. "
            f"Candidate Interests: {user_interests}. "
            f"Context Query: {query}. "
            "Follow the criteria in the system prompt to evaluate this candidate."
        )

        try:
            # We strictly use the async AIService, but this method is often called synchronously via to_thread.
            # We must handle the async call properly.
            import asyncio
            
            async def _call_ai():
                svc = AIService()
                # System prompt + User prompt
                return await svc.chat([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_prompt}
                ], model=DEFAULT_MODEL)

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Check if we are in a thread where we can verify a new loop or use run_coroutine_threadsafe
                    # But simpler: if loop is running and we are in a thread, `asyncio.run` might fail.
                    # Best approach for to_thread usage: just create a new loop if it's a dedicated thread.
                    # Safety check:
                    return asyncio.run(_call_ai()) 
            except RuntimeError:
                 return asyncio.run(_call_ai())

        except Exception as e:
            print(f"Insight Generation Error: {e}")
            return f"Insight unavailable for {user_name}."
