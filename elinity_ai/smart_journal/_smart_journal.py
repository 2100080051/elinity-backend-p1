import google.generativeai as genai
import os
from dotenv import load_dotenv
from elinity_ai.modes.prompts import SYSTEM_PROMPT_JOURNAL_INTELLIGENCE

load_dotenv()

class ElinitySmartJournal: 
    def __init__(self): 
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        # prefer the new model if set, fallback to a sensible default
        model_name = os.getenv('GOOGLE_MODEL', 'google/gemma-3-27b-it:free')
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception:
            # if the google model init fails, keep None and rely on OpenRouter fallback
            self.model = None

    async def generate_insights(self, transcript, user_profile=None):
        """Asynchronously generate AI insights from a transcript.

        This method prefers Google Gemini (if available) but falls back to
        the OpenRouter-backed `AIService` using `await` to avoid creating
        nested event loops inside an existing asyncio loop (e.g. Uvicorn).
        """
        
        profile_context = f"\nUSER CONTEXT: {user_profile}" if user_profile else ""
        prompt = f"{SYSTEM_PROMPT_JOURNAL_INTELLIGENCE}{profile_context}\n\nTRANSCRIPT TO ANALYZE:\n{transcript}"

        # First try Google Gemini (if available). Run the sync call in a thread to avoid blocking.
        try:
            if self.model is not None:
                import asyncio

                def gen_call():
                    return self.model.generate_content(prompt)

                response = await asyncio.to_thread(gen_call)
                # Some Google clients put text in different attributes; be defensive.
                try:
                    return response.text
                except Exception:
                    return str(response)
        except Exception as e:
            # Log and fall through to OpenRouter fallback
            print(f"Google Gemini generation failed: {e}")

        # Fallback to OpenRouter via AIService (async)
        try:
            from services.ai_service import AIService, DEFAULT_MODEL
            svc = AIService()
            messages = [{"role": "system", "content": prompt}]
            resp_text = await svc.chat(messages, model=DEFAULT_MODEL)
            return resp_text
        except Exception as e:
            print(f"OpenRouter fallback failed: {e}")
            return None



# if __name__ == "__main__":
#     sm_journal = SmartJournal()
#     result = sm_journal.generate_insights(text) 
#     print(result)