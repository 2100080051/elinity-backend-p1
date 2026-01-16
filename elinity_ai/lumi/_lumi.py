from typing import Dict, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage 
from langchain.memory import ConversationBufferWindowMemory
from services.ai_service import AIService
import operator
from langsmith import Client
import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class CoachingMode(Enum):
    DEEP_CONVERSATION = "deep_conversation"
    SOCRATIC_LEARNING = "socratic_learning"
    RELATIONSHIP_FLOURISHING = "relationship_flourishing"
    RELATIONSHIP_THERAPY = "relationship_therapy"
    PERSONAL_COACH = "personal_coach"
    MODE_SELECTOR = "mode_selector"

class CoachingState(TypedDict):
    messages: Annotated[List, operator.add]
    current_mode: str
    conversation_depth: int
    user_goals: List[str]
    session_context: Dict
    emotional_state: str
    relationship_context: Dict

class AICoachingSystem:
    def __init__(self, llm_model: str = None, langsmith_api_key: str = None):
        # Use shared AI service (OpenRouter) for LLM calls
        self.ai_service = AIService()
        self.memory = ConversationBufferWindowMemory(k=10)
        self.graph = self._build_graph()
        
        # Initialize LangSmith client
        self.langsmith_api_key = langsmith_api_key or os.getenv("LANGSMITH_API_KEY")
        if self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            self.langsmith_client = Client(api_key=self.langsmith_api_key)
        else:
            raise RuntimeError("Warning: LANGSMITH_API_KEY not found. Using fallback prompt.")
            
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(CoachingState)
        
        # Add nodes for each coaching mode
        workflow.add_node("mode_selector", self._mode_selector_node)
        workflow.add_node("deep_conversation", self._deep_conversation_node)
        workflow.add_node("socratic_learning", self._socratic_learning_node)
        workflow.add_node("relationship_flourishing", self._relationship_flourishing_node)
        workflow.add_node("relationship_therapy", self._relationship_therapy_node)
        workflow.add_node("personal_coach", self._personal_coach_node)
        
        # Set entry point
        workflow.set_entry_point("mode_selector")
        
        # Add conditional edges for mode routing
        workflow.add_conditional_edges(
            "mode_selector",
            self._route_to_mode,
            {
                CoachingMode.DEEP_CONVERSATION.value: "deep_conversation",
                CoachingMode.SOCRATIC_LEARNING.value: "socratic_learning",
                CoachingMode.RELATIONSHIP_FLOURISHING.value: "relationship_flourishing",
                CoachingMode.RELATIONSHIP_THERAPY.value: "relationship_therapy",
                CoachingMode.PERSONAL_COACH.value: "personal_coach",
            }
        )
        
        # Add edges back to mode selector for mode switching
        for mode in CoachingMode:
            if mode != CoachingMode.MODE_SELECTOR:
                workflow.add_edge(mode.value, END)
        
        return workflow.compile()
    
    def _mode_selector_node(self, state: CoachingState) -> Dict:
        """Analyzes user input to determine appropriate coaching mode"""
        try: 
            prompt = self.langsmith_client.pull_prompt('elinity-mode-selector')
            last_message = state["messages"][-1] if state["messages"] else ""
            formatted_prompt = prompt.format(
                user_message=last_message,
                current_mode=state.get("current_mode", "none"),
                context=state.get("session_context", {})
            )

            # Use shared AI service
            resp_text = None
            try:
                resp = self.ai_service.chat([{"role": "system", "content": formatted_prompt}])
                import asyncio
                if hasattr(resp, '__await__'):
                    resp_text = asyncio.get_event_loop().run_until_complete(resp)
                else:
                    resp_text = resp
            except Exception:
                resp_text = ""

            mode = self._extract_mode_from_response(resp_text)

            return {
                "current_mode": mode,
                "session_context": {**state.get("session_context", {}), "mode_selection_reason": resp_text}
            }
        except Exception as e:
            raise RuntimeError(f"Failed to pull mode selector prompt.")
            
    
    def _deep_conversation_node(self, state: CoachingState) -> Dict:
        """Facilitates deep, meaningful conversations"""
        try:  
            prompt = self.langsmith_client.pull_prompt('elinity-deep-conversation')
            formatted = prompt.format(
                conversation_depth=state.get("conversation_depth", 1),
                emotional_state=state.get("emotional_state", "neutral"),
                recent_messages=state["messages"][-3:] if len(state["messages"]) >= 3 else state["messages"]
            )
            try:
                resp = self.ai_service.chat([{"role": "system", "content": formatted}])
                import asyncio
                if hasattr(resp, '__await__'):
                    resp_text = asyncio.get_event_loop().run_until_complete(resp)
                else:
                    resp_text = resp
            except Exception:
                resp_text = "(ai error)"

            return {
                "messages": [AIMessage(content=resp_text)],
                "conversation_depth": min(state.get("conversation_depth", 1) + 1, 10)
            }
        except Exception as e: 
            raise RuntimeError(f"Failed to pull deep conversation prompt:{e}")
    
    def _socratic_learning_node(self, state: CoachingState) -> Dict:
        """Uses Socratic method for learning and growth"""
        try:
            prompt = self.langsmith_client.pull_prompt("elinity-socratic-mode")
            formatted = prompt.format(
                current_topic=self._extract_current_topic(state["messages"]),
                user_goals=state.get("user_goals", []),
                session_context=state.get("session_context", {})
            )
            try:
                resp = self.ai_service.chat([{"role": "system", "content": formatted}])
                import asyncio
                if hasattr(resp, '__await__'):
                    resp_text = asyncio.get_event_loop().run_until_complete(resp)
                else:
                    resp_text = resp
            except Exception:
                resp_text = "(ai error)"
            return {"messages": [AIMessage(content=resp_text)]}
        except Exception as e:
            raise RuntimeError(f"Failed to pull socratic conversation prompt:{e}")
        
    def _relationship_flourishing_node(self, state: CoachingState) -> Dict:
        try:
            """Focuses on building and strengthening relationships"""
            prompt = self.langsmith_client.pull_prompt("elinity-relationship-fourish-mode")
            formatted = prompt.format(
                relationship_context=state.get("relationship_context", {}),
                current_focus=self._extract_relationship_focus(state["messages"]),
                strengths=state.get("session_context", {}).get("relationship_strengths", [])
            )
            try:
                resp = self.ai_service.chat([{"role": "system", "content": formatted}])
                import asyncio
                if hasattr(resp, '__await__'):
                    resp_text = asyncio.get_event_loop().run_until_complete(resp)
                else:
                    resp_text = resp
            except Exception:
                resp_text = "(ai error)"
            return {"messages": [AIMessage(content=resp_text)]}
        except Exception as e:
            raise RuntimeError(f"Relationship fourish node")
    
    def _relationship_therapy_node(self, state: CoachingState) -> Dict:
        """Addresses relationship conflicts and therapeutic issues"""
        try: 
            prompt = self.langsmith_client.pull_prompt("elinity-therapy-mode")
            formatted = prompt.format(
                relationship_issues=self._extract_relationship_issues(state["messages"]),
                emotional_state=state.get("emotional_state", "neutral"),
                communication_patterns=state.get("session_context", {}).get("communication_patterns", [])
            )
            try:
                resp = self.ai_service.chat([{"role": "system", "content": formatted}])
                import asyncio
                if hasattr(resp, '__await__'):
                    resp_text = asyncio.get_event_loop().run_until_complete(resp)
                else:
                    resp_text = resp
            except Exception:
                resp_text = "(ai error)"
            return {"messages": [AIMessage(content=resp_text)]}
        except Exception as e:
            raise RuntimeError(f"Error in pulling prompt for therapy mode.")
    
    def _personal_coach_node(self, state: CoachingState) -> Dict:
        """Provides personal coaching for goals and development"""
        try: 
            prompt = self.langsmith_client.pull_prompt("elinity-personal-coach-mode")
            formatted = prompt.format(
                user_goals=state.get("user_goals", []),
                progress=state.get("session_context", {}).get("progress", []),
                challenges=state.get("session_context", {}).get("challenges", []),
                strengths=state.get("session_context", {}).get("strengths", [])
            )
            try:
                resp = self.ai_service.chat([{"role": "system", "content": formatted}])
                import asyncio
                if hasattr(resp, '__await__'):
                    resp_text = asyncio.get_event_loop().run_until_complete(resp)
                else:
                    resp_text = resp
            except Exception:
                resp_text = "(ai error)"
            return {"messages": [AIMessage(content=resp_text)]}
        except Exception as e:
            raise RuntimeError(f"Error in pulling prompt for personal coach node")
        
    def _route_to_mode(self, state: CoachingState) -> str:
        """Routes to the appropriate coaching mode"""
        return state.get("current_mode", CoachingMode.DEEP_CONVERSATION.value)
    
    def _extract_mode_from_response(self, response: str) -> str:
        """Extract mode from LLM response (simplified)"""
        response_lower = response.lower()
        for mode in CoachingMode:
            if mode.value in response_lower:
                return mode.value
        return CoachingMode.DEEP_CONVERSATION.value
    
    def _extract_current_topic(self, messages: List) -> str:
        """Extract current conversation topic"""
        if not messages:
            return "general conversation"
        return "current discussion topic"  # Would implement topic extraction
    
    def _extract_relationship_focus(self, messages: List) -> str:
        """Extract relationship focus area"""
        return "communication and connection"  # Would implement focus extraction
    
    def _extract_relationship_issues(self, messages: List) -> List[str]:
        """Extract relationship issues mentioned"""
        return []  # Would implement issue extraction
    
    def process_message(self, user_message: str, current_state: Optional[CoachingState] = None) -> Dict:
        """Process a user message through the coaching system"""
        if current_state is None:
            current_state = {
                "messages": [HumanMessage(content=user_message)],
                "current_mode": "",
                "conversation_depth": 1,
                "user_goals": [],
                "session_context": {},
                "emotional_state": "neutral",
                "relationship_context": {}
            }
        else:
            current_state["messages"].append(HumanMessage(content=user_message))
        
        result = self.graph.invoke(current_state)
        return result

