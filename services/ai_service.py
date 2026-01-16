import os
import httpx
from typing import Optional

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Primary model per requirements (use the OpenRouter model alias requested)
DEFAULT_MODEL = "openai/gpt-oss-20b:free"


class AIService:
    """Simple AI service wrapper for OpenRouter chat completions.

    The implementation is intentionally small and defensive: it reads the
    API key from OPENROUTER_API_KEY, sends the messages payload described
    in the task, and returns the assistant message text.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")

    async def chat(self, prompt: Optional[object], user_input: Optional[str] = None, model: Optional[str] = None, api_key: Optional[str] = None) -> str:
        """Send either a system prompt (string) + optional user_input or a full messages list.

        - If `prompt` is a list, it's treated as the messages payload and sent as-is.
        - If `prompt` is a string, it's used as the system message and `user_input` becomes the user message.
        """

        key = api_key or self.api_key
        if not key:
            print("OPENROUTER_API_KEY is not set. Returning fallback response.")
            return "(no API key) Let's start your training."

        if isinstance(prompt, list):
            messages = prompt
        else:
            messages = [
                {"role": "system", "content": str(prompt)},
                {"role": "user", "content": user_input or "Start the training session."},
            ]

        model_to_use = model or DEFAULT_MODEL
        payload = {"model": model_to_use, "messages": messages}

        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        except Exception as e:
            print(f"OpenRouter request failed: {e}")
            return "(error) The AI service is currently unavailable."

        if resp.status_code != 200:
            # Print debug info and return a readable error-like message
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            print(f"OpenRouter API error: status={resp.status_code}, body={body}")
            return f"(ai error {resp.status_code}) The AI did not return a valid response."

        try:
            data = resp.json()
            # Typical OpenRouter response mirrors OpenAI-style completions
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Failed to parse OpenRouter response: {e} -- raw: {resp.text}")
            return "(error) Unable to parse AI response."


async def ask_llm(prompt: str, model: Optional[str] = None, api_key: Optional[str] = None) -> str:
    """Shared convenience function for questions to the LLM.

    Other modules should call `await ask_llm(prompt)` to get a string reply.
    This ensures a single place controls the primary model and API key.
    """
    svc = AIService()
    # The AIService.chat already accepts either a messages list or a system prompt string.
    return await svc.chat(prompt, model=model, api_key=api_key)
