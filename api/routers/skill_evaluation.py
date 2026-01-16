from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from database.session import async_session
from models.conversation import ConversationSession, ConversationTurn
from services.ai_service import AIService, DEFAULT_MODEL
from core.universal_prompt_evaluation import UNIVERSAL_EVALUATION_PROMPT
from models.evaluation import EvaluationReport
from pathlib import Path
import json
import os
import json as pyjson

router = APIRouter()
ai_service = AIService()

# Simple in-memory cache for evaluation reports (keeps solution self-contained).
_REPORT_CACHE: Dict[str, Dict[str, Any]] = {}


def _load_skill_file(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _find_skill_in_file(skills: List[Dict[str, Any]], skill_id: int) -> Optional[Dict[str, Any]]:
    for s in skills:
        try:
            if int(s.get("id")) == int(skill_id):
                return s
        except Exception:
            continue
    return None


async def _gather_transcript(session_id: str) -> str:
    async with async_session() as session:
        q = select(ConversationTurn).where(ConversationTurn.session_id == session_id).order_by(ConversationTurn.timestamp.asc())
        res = await session.execute(q)
        turns = [t for (t,) in res.fetchall()]
    # Simple transcript format
    transcript_lines = [f"{turn.role.upper()}: {turn.content}" for turn in turns]
    return "\n".join(transcript_lines)


@router.post("/session/{session_id}")
async def evaluate_session(session_id: str, session_type: Optional[str] = Query(None)):
    # Load session
    async with async_session() as db:
        q = select(ConversationSession).where(ConversationSession.id == session_id)
        res = await db.execute(q)
        row = res.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found")
        conv: ConversationSession = row[0]

    # Determine skill metadata source
    skill = None
    base = Path(__file__).resolve().parents[2] / "data"
    if conv.skill_type == "relationship":
        skills = _load_skill_file(base / "relationship_skills.json")
        skill = _find_skill_in_file(skills, conv.skill_id)
    elif conv.skill_type == "self-growth":
        skills = _load_skill_file(base / "self_growth_skills.json")
        skill = _find_skill_in_file(skills, conv.skill_id)
    elif conv.skill_type == "social":
        skills = _load_skill_file(base / "social_skills.json")
        skill = _find_skill_in_file(skills, conv.skill_id)

    skill_title = skill.get("name") if skill else "Unknown Skill"
    skill_description = skill.get("description") if skill else ""

    sess_type = session_type or "text"
    transcript = await _gather_transcript(session_id)

    # Build prompt: use universal evaluation prompt as system, then provide structured user content
    system_prompt = UNIVERSAL_EVALUATION_PROMPT
    user_payload = (
        f"Skill Title: {skill_title}\nSkill Description: {skill_description}\nSession Type: {sess_type}\nSession Transcript:\n{transcript}"
    )

    # choose model
    if sess_type == "video":
        model_name = "nvidia/nemotron-nano-12b-v2-vl:free"
    else:
        model_name = DEFAULT_MODEL

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_payload}]

    ai_response = await ai_service.chat(messages, model=model_name, api_key=os.getenv("OPENROUTER_API_KEY"))

    # Try to parse JSON out of response; tolerant
    parsed = None
    try:
        parsed = pyjson.loads(ai_response)
    except Exception:
        # If parsing fails, leave parsed as None
        parsed = None

    report = {"summary": ai_response if parsed is None else (parsed.get("summary") if isinstance(parsed, dict) else None), "evaluation": parsed}

    # Persist report to DB (fall back to in-memory cache on error)
    try:
        async with async_session() as db:
            ev = EvaluationReport(session_id=session_id, skill_id=str(conv.skill_id) if conv and conv.skill_id is not None else None, skill_type=conv.skill_type if conv else None, evaluation_json=parsed if parsed is not None else {"raw": ai_response})
            db.add(ev)
            await db.commit()
            await db.refresh(ev)
            # Return stored record representation
            return {"summary": report.get("summary"), "evaluation": report.get("evaluation"), "report_id": str(ev.id)}
    except Exception as e:
        # DB unavailable or error — fall back to cache
        print(f"Failed to persist evaluation report to DB: {e}")
        _REPORT_CACHE[session_id] = report
        return report


@router.post("/direct")
async def evaluate_direct(payload: Dict[str, Any] = Body(...)):
    title = payload.get("skill_title", "Untitled")
    desc = payload.get("skill_description", "")
    sess_type = payload.get("session_type", "text")
    transcript = payload.get("transcript", "")

    system_prompt = UNIVERSAL_EVALUATION_PROMPT
    user_payload = f"Skill Title: {title}\nSkill Description: {desc}\nSession Type: {sess_type}\nSession Transcript:\n{transcript}"

    if sess_type == "video":
        model_name = "nvidia/nemotron-nano-12b-v2-vl:free"
    else:
        model_name = DEFAULT_MODEL

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_payload}]

    ai_response = await ai_service.chat(messages, model=model_name, api_key=os.getenv("OPENROUTER_API_KEY"))

    parsed = None
    try:
        parsed = pyjson.loads(ai_response)
    except Exception:
        parsed = None

    report = {"summary": ai_response if parsed is None else (parsed.get("summary") if isinstance(parsed, dict) else None), "evaluation": parsed}

    # Try to persist (no session_id for direct evaluations)
    try:
        async with async_session() as db:
            ev = EvaluationReport(session_id=None, skill_id=title, skill_type=sess_type, evaluation_json=parsed if parsed is not None else {"raw": ai_response})
            db.add(ev)
            await db.commit()
            await db.refresh(ev)
            return {"summary": report.get("summary"), "evaluation": report.get("evaluation"), "report_id": str(ev.id)}
    except Exception as e:
        print(f"Failed to persist direct evaluation report to DB: {e}")
        # fallback
        return report


@router.get("/{session_id}/report")
async def get_report(session_id: str):
    # Try DB first
    try:
        async with async_session() as db:
            q = select(EvaluationReport).where(EvaluationReport.session_id == session_id)
            res = await db.execute(q)
            row = res.fetchone()
            if row:
                ev: EvaluationReport = row[0]
                return {"report_id": str(ev.id), "session_id": str(ev.session_id) if ev.session_id else None, "skill_id": ev.skill_id, "skill_type": ev.skill_type, "evaluation": ev.evaluation_json, "created_at": ev.created_at.isoformat() if ev.created_at is not None else None}
    except Exception as e:
        print(f"DB read failed for evaluation report: {e}")

    # Fallback to cache
    rep = _REPORT_CACHE.get(session_id)
    if not rep:
        raise HTTPException(status_code=404, detail="No evaluation report found for this session")
    return rep
