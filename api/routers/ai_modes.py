from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
# Placeholder imports for core logic
from utils.token import get_current_user
from models.user import Tenant

from pydantic import BaseModel
router = APIRouter(tags=["AI Modes"])

class StartModeSchema(BaseModel):
    message: str

from elinity_ai.modes.prompts import (
    SYSTEM_PROMPT_PODCAST, SYSTEM_PROMPT_MEDITATION, SYSTEM_PROMPT_DEEP_THINKING,
    SYSTEM_PROMPT_VISUALIZATION, SYSTEM_PROMPT_METACOGNITION, SYSTEM_PROMPT_MINDFULNESS,
    SYSTEM_PROMPT_SOCRATIC, SYSTEM_PROMPT_LEARNING, SYSTEM_PROMPT_PEP_TALK,
    SYSTEM_PROMPT_REALITY_CHECK, SYSTEM_PROMPT_REFLECTION, SYSTEM_PROMPT_COUPLE_BESTIE,
    PERSONA_TOUGH_LOVE, PERSONA_EMPATHETIC_THERAPIST, PERSONA_SASSY_FRIEND,
    PERSONA_WISE_ELDER, PERSONA_HYPE_COACH, PERSONA_EFFICIENCY_STRATEGIST,
    PERSONA_ZEN_MASTER, PERSONA_PHILOSOPHER, PERSONA_JOKEY_COACH,
    PERSONA_AI_ORACLE, PERSONA_LOGIC_MASTER,
    HISTORICAL_SOCRATES, HISTORICAL_JUNG, HISTORICAL_NIETZSCHE,
    HISTORICAL_DA_VINCI, HISTORICAL_MUSASHI, HISTORICAL_AURELIUS,
    HISTORICAL_WOOLF, HISTORICAL_WATTS
)

from api.routers._llm import safe_chat_completion

@router.post("/{mode_name}/start")
async def start_mode_session(mode_name: str, payload: StartModeSchema, current_user: Tenant = Depends(get_current_user)):
    """Start or continue a session in a specific AI mode."""
    message = payload.message
    valid_modes = {
        "podcast": SYSTEM_PROMPT_PODCAST,
        "meditation": SYSTEM_PROMPT_MEDITATION,
        "deep_thinking": SYSTEM_PROMPT_DEEP_THINKING,
        "visualization": SYSTEM_PROMPT_VISUALIZATION,
        "metacognition": SYSTEM_PROMPT_METACOGNITION,
        "mindfulness": SYSTEM_PROMPT_MINDFULNESS,
        "socratic": SYSTEM_PROMPT_SOCRATIC,
        "learning": SYSTEM_PROMPT_LEARNING,
        "pep_talk": SYSTEM_PROMPT_PEP_TALK,
        "reality_check": SYSTEM_PROMPT_REALITY_CHECK,
        "weekly_reflection": SYSTEM_PROMPT_REFLECTION,
        "monthly_reflection": SYSTEM_PROMPT_REFLECTION,
        "reflection": SYSTEM_PROMPT_REFLECTION,
        "couple_bestie": SYSTEM_PROMPT_COUPLE_BESTIE,
        # Personas
        "tough_love": PERSONA_TOUGH_LOVE,
        "empathetic": PERSONA_EMPATHETIC_THERAPIST,
        "sassy": PERSONA_SASSY_FRIEND,
        "wise_elder": PERSONA_WISE_ELDER,
        "hype": PERSONA_HYPE_COACH,
        "efficiency": PERSONA_EFFICIENCY_STRATEGIST,
        "zen": PERSONA_ZEN_MASTER,
        "philosopher": PERSONA_PHILOSOPHER,
        "joker": PERSONA_JOKEY_COACH,
        "oracle": PERSONA_AI_ORACLE,
        "logic": PERSONA_LOGIC_MASTER,
        # Historical
        "socrates_historical": HISTORICAL_SOCRATES,
        "jung": HISTORICAL_JUNG,
        "nietzsche": HISTORICAL_NIETZSCHE,
        "da_vinci": HISTORICAL_DA_VINCI,
        "musashi": HISTORICAL_MUSASHI,
        "aurelius": HISTORICAL_AURELIUS,
        "woolf": HISTORICAL_WOOLF,
        "watts": HISTORICAL_WATTS,
        # Standard fallbacks
        "coach": PERSONA_TOUGH_LOVE,
        "therapist": PERSONA_EMPATHETIC_THERAPIST,
        "game_creator": "You are a game designer. Help the user create a new game concept with rules.",
        "lumi": "You are Lumi, a helpful and wise AI companion."
    }
    
    if mode_name not in valid_modes:
        raise HTTPException(404, f"Mode '{mode_name}' not found")
        
    system_prompt = valid_modes[mode_name]
    
    # Call Real LLM
    response = await safe_chat_completion(
        system=system_prompt,
        user_prompt=message,
        max_tokens=500
    )
    
    return {"mode": mode_name, "ai_message": response}

import json
from pathlib import Path

# Load Registry
REGISTRY_PATH = Path('data/game_registry.json')
GAME_REGISTRY = []

def load_registry():
    global GAME_REGISTRY
    if REGISTRY_PATH.exists():
        try:
            GAME_REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))
        except Exception: 
            GAME_REGISTRY = []

load_registry()

@router.get("/games/list", tags=["AI Modes"])
async def list_games():
    """Return list of integrated games."""
    if not GAME_REGISTRY:
        load_registry()
    return {"games": GAME_REGISTRY}

@router.post("/games/recommend", tags=["AI Modes"])
async def recommend_game(query: str):
    """Recommend a game based on user query/mood."""
    if not GAME_REGISTRY:
        load_registry()
    
    # 1. Construct context for LLM
    game_list_str = "\n".join([f"- {g['title']} (ID: {g['id']}): {g.get('description', '')} [Tags: {', '.join(g.get('tags', []))}]" for g in GAME_REGISTRY])
    
    system = "You are a Game Recommendation Engine. Pick the best single game from the list below based on the user's mood or request. Return ONLY the JSON object of the chosen game."
    prompt = f"User Query: {query}\n\nAvailable Games:\n{game_list_str}\n\nWhich game is best? Return JSON."
    
    # 2. Call LLM
    try:
        response = await safe_chat_completion(system, prompt, temperature=0.3, max_tokens=150)
        # simplistic parsing/fallback
        # Ideally we parse JSON. For robustness, let's just search for the ID or title in response or fall back to keyword search.
        
        # Fallback keyword search if LLM fails or is skipped
        scores = []
        q_lower = query.lower()
        for g in GAME_REGISTRY:
            score = 0
            if g['id'].replace('-', ' ') in q_lower: score += 5
            if g['title'].lower() in q_lower: score += 5
            if any(t.lower() in q_lower for t in g.get('tags', [])): score += 2
            scores.append((score, g))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        best_match = scores[0][1]
        
        return {"recommendation": best_match, "reasoning": response}
        
    except Exception:
        # Fallback to random or first
        import random
        return {"recommendation": random.choice(GAME_REGISTRY) if GAME_REGISTRY else None, "reasoning": "Random pick due to error."}

