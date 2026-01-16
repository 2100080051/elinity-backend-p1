from typing import List, Optional
import os
import json
from ._prompts import ONBOARD_PROMPT
from pydantic import BaseModel
from services.ai_service import AIService, ask_llm

class ConversationChat(BaseModel):
    role: str = "system" # "user" or "assistant"
    content: str

class ContinueConversation(BaseModel):
    user_message: str
    asset_url: Optional[str] = None

# Elinity AI Implementation
def welcome_message():
    """Return the welcome message to initialize the conversation."""
    return "Hello! I'm ElinityAI, your personal social connection guide. I'm here to get to know you better so I can help you find meaningful connections. Let's have a relaxed conversation. Could you start by telling me a little about yourself?"

class ElinityOnboardingConversation:
    def __init__(self, model_name=None, system_prompt=ONBOARD_PROMPT, api_key=None, welcome_message="", generation_config=None, safety_settings=None, conversation_history=None):
        """Lightweight onboarding conversation powered by OpenRouter via `services.ai_service`.
    
        Args:
            custom_api_key: Optional API key to override the one in .env file
            
        Returns:
            bool: True if configuration was successful
        Variables: 
            model_name: The name of the model to use
            system_prompt: The system prompt to use
            api_key: The API key to use
            chat: The chat object
            session_end: Whether the session has ended
            current_question_index: The index of the current question
            conversation_history: List of conversation messages i.e List[ConversationChat]
        Raises:
            ValueError: If no API key is available
        """ 
        self.generation_config = generation_config or {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 150,
        }

        self.welcome_message = welcome_message or "Hello! I'm ElinityAI, your personal social connection guide. I'm here to get to know you better so I can help you find meaningful connections. Let's have a relaxed conversation. Could you start by telling me a little about yourself?"

        # Use the shared AI service (OpenRouter). The AIService will check OPENROUTER_API_KEY.
        self.ai_service = AIService()
        self.system_prompt = system_prompt
        self.session_end = False
        self.current_question_index = 0
        self.conversation_history: List[ConversationChat] = conversation_history or []

        # Add welcome message to conversation history
        self.add_message(self.welcome_message)
        
    def parse_histories(self):
        return [chat.model_dump() for chat in self.conversation_history]
        
    def add_message(self,content,role="system"):
        '''Add to conversation history.'''
        chat = ConversationChat(role=role,content=content)
        self.conversation_history.append(chat) 
    
    def get_next_prompt(self,user_message):
        """Get the next prompt from Gemini based on the user's message."""
        if not user_message:
            return "I didn't catch that. Could you please repeat?"

        # Add user message to history
        self.add_message(role="user", content=user_message)

        # Build prompt for the LLM: include system prompt and user message
        message_with_reminder = f"{user_message}\n\nRemember to keep your response very brief (1-3 sentences) and conversational."
        messages = [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": message_with_reminder}]

        # Call shared ask_llm helper (uses OpenRouter + gpt-oss-20b by default)
        try:
            assistant_response = None
            # prefer the instance method which handles missing API key gracefully
            assistant_response = self.ai_service.chat(messages)
            # ai_service.chat is async; ensure we await result if needed
            if hasattr(assistant_response, '__await__'):
                import asyncio
                assistant_response = asyncio.get_event_loop().run_until_complete(assistant_response)
        except Exception:
            # As a fallback, return a safe short reply
            return "Sorry, I'm having trouble responding right now."

        # Record assistant response
        self.add_message(assistant_response, role="assistant")
        return assistant_response


    def extract_profile_from_text(self, text: str) -> dict:
        """Use the LLM to extract profile fields (age, interests, preferences, favorites).

        Returns a dict with keys: age, interests, preferences, favorites. Values are best-effort.
        """
        prompt = (
            "Extract the user's basic profile information from the following text. "
            "Return a JSON object with keys: age (number or null), interests (list of strings), "
            "hobbies (list of strings), preferences (free-text), favorites (list of strings). "
            "If a field cannot be determined, use null or empty list.\n\nText:\n" + text
        )
        try:
            # ask_llm is async; call the instance method for graceful fallback
            response = None
            response = self.ai_service.chat([{"role": "system", "content": prompt}], model=None)
            if hasattr(response, '__await__'):
                import asyncio
                response = asyncio.get_event_loop().run_until_complete(response)
            # try parse JSON
            parsed = None
            try:
                parsed = json.loads(response)
            except Exception:
                # Attempt to find simple patterns
                parsed = {"age": None, "interests": [], "hobbies": [], "preferences": "", "favorites": []}
            return parsed
        except Exception:
            return {"age": None, "interests": [], "hobbies": [], "preferences": "", "favorites": []}

    def start_conversation(self):
        # Add welcome message to the user 
        self.add_message(self.welcome_message)
        return self.conversation_history 
    
    def get_welcome_message(self):
        return self.parse_histories()[0]
    
    def get_model_list(self): 
        """
        Returns:
           List[GenerativeModel]: The list of available generative AI models
        """
        # Return configured primary model name (best-effort)
        try:
            return [os.getenv("OPENROUTER_MODEL", "gpt-oss-20b")]
        except Exception:
            return ["gpt-oss-20b"]
    
    
try:
    model = ElinityOnboardingConversation()
except Exception:
    # If configuration (API keys) is missing, allow import to succeed and
    # expose `model` as None. Callers should check and fail gracefully.
    model = None