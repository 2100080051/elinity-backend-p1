from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from ._system_prompt import load_system_prompt
from ._llm import safe_chat_completion
import uuid
from ._system_prompt import load_system_prompt

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


class StartReq(BaseModel):
    host: str
    players: List[str]


class AddPairReq(BaseModel):
    session: Dict[str, Any]
    contentA: str
    contentB: str


class RevealReq(BaseModel):
    session: Dict[str, Any]
    pairId: str


class FinalizeReq(BaseModel):
    session: Dict[str, Any]


@router.post('/start_game')
async def route_start(req: StartReq):
    if not req.players:
        raise HTTPException(status_code=400, detail='players required')
    session = {
        'id': str(uuid.uuid4()),
        'host': req.host,
        'players': req.players,
        'pairs': [],
        'revealed': [],
    }
    prompt = load_system_prompt('memory-match-maker', default='You design simple memory match pairs and playful hints.')
    return { 'message': 'game started', 'session': session, 'promptLoaded': bool(prompt) }


@router.post('/add_pair')
async def route_add_pair(req: AddPairReq):
    session = req.session
    if not session:
        raise HTTPException(status_code=400, detail='missing session')
    pid = str(uuid.uuid4())
    pair = { 'id': pid, 'a': req.contentA, 'b': req.contentB, 'revealed': False }
    session.setdefault('pairs', []).append(pair)
    return { 'pair': pair, 'session': session }


@router.post('/reveal_pair')
async def route_reveal(req: RevealReq):
    session = req.session
    pid = req.pairId
    if not session or not pid:
        raise HTTPException(status_code=400, detail='missing data')
    for p in session.get('pairs', []):
        if p.get('id') == pid:
            p['revealed'] = True
            session.setdefault('revealed', []).append(pid)
            return { 'pair': p, 'session': session }
    raise HTTPException(status_code=404, detail='pair not found')


@router.post('/finalize_game')
async def route_finalize(req: FinalizeReq):
    session = req.session
    if not session:
        raise HTTPException(status_code=400, detail='missing session')
    total = len(session.get('pairs', []))
    revealed = len(session.get('revealed', []))
    summary = f"You revealed {revealed}/{total} pairs. Nice memory work!"
    system_prompt = load_system_prompt('memory-match-maker', default='You summarize quick memory-match games in a playful friendly tone.')
    if total > 0:
        prompt = f"Summarize a quick memory match game: {revealed}/{total} pairs revealed. Provide a 1-sentence fun summary."
        try:
            summary = await safe_chat_completion(system_prompt or '', prompt, temperature=0.8, max_tokens=80, fallback=summary)
        except Exception:
            pass

    return { 'summary': summary, 'session': session }
