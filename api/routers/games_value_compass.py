from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests
from typing import List, Optional, Dict, Any
from pathlib import Path
from ._system_prompt import load_system_prompt as _load_system_prompt

router = APIRouter()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_FALLBACK_MODELS = ["groq/compound", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]


def get_model_candidates() -> List[str]:
    env_model = os.getenv("GROQ_MODEL")
    lst = []
    if env_model:
        lst.append(env_model)
    for m in DEFAULT_FALLBACK_MODELS:
        if m not in lst:
            lst.append(m)
    return lst


def load_system_prompt() -> str:
    # delegate to shared loader but keep the original inline default
    return _load_system_prompt('value-compass', default="You are the Game Master for Values Compass.")


class SubmitAnswersRequest(BaseModel):
    dilemma: str
    p1Answer: str
    p2Answer: str
    history: Optional[List[Dict[str, Any]]] = None
    round: Optional[int] = 1


class NextDilemmaRequest(BaseModel):
    round: Optional[int] = 1
    history: Optional[List[Dict[str, Any]]] = None


class EndGameRequest(BaseModel):
    history: Optional[List[Dict[str, Any]]] = None


# --- Mock helpers (same simple heuristics as the original JS)

def mock_comparison(dilemma: str, p1: str, p2: str) -> Dict[str, str]:
    similar = (p1.lower().find(p2.lower().split(" ")[0]) != -1) or (p2.lower().find(p1.lower().split(" ")[0]) != -1)
    if similar:
        comparison = f"Both of you seem to value similar priorities here. This alignment shows a shared perspective on {' '.join(dilemma.split(' ')[:5])}."
    else:
        comparison = f"Interesting difference! Player 1 leans toward one value, while Player 2 prioritizes another. This diversity can enrich your understanding of each other."
    follow_up = "What personal experience shaped your answer?"
    return {"comparison": comparison, "followUp": follow_up}


def mock_dilemma(round_num: int) -> str:
    dilemmas = [
        'Would you rather have unlimited time or unlimited money?',
        'What matters more: being respected or being loved?',
        'Would you prioritize personal freedom or collective security?',
        'Which is more important: honesty or kindness?',
        'Would you rather be known for your intelligence or your compassion?',
        'What drives you more: curiosity or stability?',
        'Would you choose a life of adventure with uncertainty or comfort with routine?'
    ]
    idx = max(0, min(round_num - 1, len(dilemmas) - 1))
    return dilemmas[idx]


def mock_summary(history: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    hist = history or []
    total = len(hist)
    if total == 0:
        return {"alignment": 0, "insights": "No rounds completed.", "areas": ""}
    import random

    alignment = int(60 + random.random() * 30)
    insights = f"You completed {total} dilemmas together. Your answers show a healthy mix of alignment and diversity, which is great for mutual growth."
    areas = "Both of you value honesty and compassion. You differ slightly on risk tolerance and adventure."
    return {"alignment": alignment, "insights": insights, "areas": areas}


# --- Router handlers

@router.post("/submit_answers")
def submit_answers(body: SubmitAnswersRequest):
    if not body.dilemma or not body.p1Answer or not body.p2Answer:
        raise HTTPException(status_code=400, detail="dilemma, p1Answer, p2Answer required")

    system_prompt = load_system_prompt()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY:
        return mock_comparison(body.dilemma, body.p1Answer, body.p2Answer)

    # Build context
    context = f"Round {body.round}\nDilemma: {body.dilemma}\nPlayer 1 answered: \"{body.p1Answer}\"\nPlayer 2 answered: \"{body.p2Answer}\"\n\n"
    if isinstance(body.history, list) and len(body.history) > 0:
        context += "Previous rounds for context:\n"
        for r in body.history:
            context += f"- {r.get('dilemma')}: P1 said \"{r.get('p1Answer')}\", P2 said \"{r.get('p2Answer')}\"\n"

    user_prompt = f"{context}\n\nPlease:\n1. Compare the two answers and highlight where they align or differ.\n2. Offer a gentle insight about what these values might mean.\n3. Ask a thoughtful follow-up question to spark deeper discussion.\n\nFormat:\nComparison: <your comparison>\nFollow-up: <your question>"

    models = get_model_candidates()
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    for model in models:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "max_tokens": 400,
                "temperature": 0.8,
            }
            resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")

            lines = [l.strip() for l in content.split("\n") if l.strip()]
            comparison = ""
            follow_up = ""
            for line in lines:
                low = line.lower()
                if low.startswith('comparison:'):
                    comparison = line.split(':', 1)[1].strip()
                elif low.startswith('follow-up:') or low.startswith('follow up:'):
                    follow_up = line.split(':', 1)[1].strip()
            if not comparison:
                comparison = ' '.join(content.split('\n')[:3]).strip()
            if not follow_up:
                follow_up = 'What made you choose that answer?'

            return {"comparison": comparison, "followUp": follow_up}
        except requests.RequestException as e:
            # try next model on specific model-not-found like errors
            try:
                err = e.response.json()
                code = err.get('code') or err.get('error', {}).get('code')
                if code == 'model_not_found':
                    continue
            except Exception:
                pass
            break

    # fallback
    return mock_comparison(body.dilemma, body.p1Answer, body.p2Answer)


@router.post("/next_dilemma")
def next_dilemma(body: NextDilemmaRequest):
    system_prompt = load_system_prompt()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY:
        return {"dilemma": mock_dilemma(body.round or 1)}

    if isinstance(body.history, list) and len(body.history) > 0:
        context = 'Previous rounds:\n'
        for r in body.history:
            context += f"- Dilemma: {r.get('dilemma')}\n  P1: {r.get('p1Answer')}\n  P2: {r.get('p2Answer')}\n"
    else:
        context = 'This is the first round.'

    user_prompt = f"{context}\n\nPlease pose a new meaningful dilemma for round {body.round}. Use a \"Would you rather...\" or \"What matters more...\" format. Keep it concise and thought-provoking."

    models = get_model_candidates()
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    for model in models:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "max_tokens": 200,
                "temperature": 0.85,
            }
            resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
            dilemma = content.strip().split('\n')[0].strip()
            dilemma = dilemma.strip('"\'')
            return {"dilemma": dilemma}
        except requests.RequestException as e:
            try:
                err = e.response.json()
                code = err.get('code') or err.get('error', {}).get('code')
                if code == 'model_not_found':
                    continue
            except Exception:
                pass
            break

    return {"dilemma": mock_dilemma(body.round or 1)}


@router.post("/end_game")
def end_game(body: EndGameRequest):
    history = body.history or []
    system_prompt = load_system_prompt()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY or not isinstance(history, list) or len(history) == 0:
        return mock_summary(history)

    # Build full game context
    context = 'Full game history:\n'
    for r in history:
        context += f"\nDilemma: {r.get('dilemma')}\nPlayer 1: {r.get('p1Answer')}\nPlayer 2: {r.get('p2Answer')}\nAI Comparison: {r.get('comparison')}\n"

    user_prompt = f"{context}\n\nPlease provide a final summary:\n1. Calculate an overall alignment percentage (0-100%) based on how similar their values are across all dilemmas.\n2. Share key insights about their relationship, collaboration, or friendship based on their answers.\n3. Highlight specific areas of connection where they strongly align.\n\nFormat:\nAlignment: <percentage>\nInsights: <your insights>\nAreas: <areas of connection>"

    models = get_model_candidates()
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    for model in models:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                "max_tokens": 600,
                "temperature": 0.75,
            }
            resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")

            lines = [l.strip() for l in content.split('\n') if l.strip()]
            alignment = 0
            insights = ''
            areas = ''
            for line in lines:
                low = line.lower()
                if low.startswith('alignment:'):
                    import re

                    m = re.search(r"\d+", line)
                    if m:
                        alignment = int(m.group(0))
                elif low.startswith('insights:'):
                    insights = line.split(':', 1)[1].strip()
                elif low.startswith('areas:'):
                    areas = line.split(':', 1)[1].strip()
            if not insights:
                insights = ' '.join(content.split('\n')[1:4]).strip()
            if not areas:
                areas = 'You share common ground on several key values.'

            return {"alignment": alignment, "insights": insights, "areas": areas}
        except requests.RequestException as e:
            try:
                err = e.response.json()
                code = err.get('code') or err.get('error', {}).get('code')
                if code == 'model_not_found':
                    continue
            except Exception:
                pass
            break

    # fallback
    return mock_summary(history)
