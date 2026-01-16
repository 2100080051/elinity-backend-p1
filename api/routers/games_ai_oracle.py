from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion

router = APIRouter()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL')

DEFAULT_MODELS = ['openai/gpt-3.5-turbo']

def get_model_candidates():
    lst = []
    if OPENROUTER_MODEL:
        lst.append(OPENROUTER_MODEL)
    for m in DEFAULT_MODELS:
        if m not in lst:
            lst.append(m)
    return lst


class QueryReq(BaseModel):
    session_id: str
    query: Optional[str] = None


@router.post('/query')
async def query(req: QueryReq):
    slug = 'ai-oracle'
    system = load_system_prompt(slug)
    prompt = req.query or 'Offer a cryptic but helpful hint about making a difficult choice.'
    fallback = 'Seek the path where your curiosity leads you.'
    try:
        answer = await safe_chat_completion(system or '', prompt, temperature=0.8, max_tokens=200, fallback=fallback)
        return {'ok': True, 'answer': answer}
    except Exception:
        return {'ok': True, 'answer': fallback}
