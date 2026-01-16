from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from database.session import get_db
from models.user import Tenant
from models.tools import GoalRitual, Nudge, Moodboard, PhotoJournal, Quiz
from schemas.tools import (
    GoalRitualCreate, GoalRitualResponse,
    MoodboardCreate, MoodboardResponse,
    PhotoJournalCreate, PhotoJournalResponse,
    QuizCreate, QuizResponse,
    NudgeResponse
)
from utils.token import get_current_user

router = APIRouter(tags=["Tools"])

# --- RITUALS ---
@router.post("/rituals", response_model=GoalRitualResponse)
async def create_ritual(ritual: GoalRitualCreate, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    db_ritual = GoalRitual(tenant=current_user.id, **ritual.model_dump())
    db.add(db_ritual)
    db.commit(); db.refresh(db_ritual)
    return db_ritual

@router.get("/rituals", response_model=List[GoalRitualResponse])
async def list_rituals(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    return db.query(GoalRitual).filter(GoalRitual.tenant == current_user.id).all()

@router.post("/rituals/{id}/complete", response_model=GoalRitualResponse)
async def complete_ritual(id: str, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    ritual = db.query(GoalRitual).filter(GoalRitual.id == id, GoalRitual.tenant == current_user.id).first()
    if not ritual: raise HTTPException(404, "Ritual not found")
    
    # Update logic: Increment streak, add to history
    # Simply appending today's date for MVP
    today = datetime.now(timezone.utc).isoformat()
    ritual.streak_count += 1
    new_history = list(ritual.history)
    new_history.append(today)
    ritual.history = new_history
    
    db.commit(); db.refresh(ritual)
    return ritual

# --- MOODBOARDS ---
@router.post("/moodboards", response_model=MoodboardResponse)
async def create_moodboard(mb: MoodboardCreate, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    db_mb = Moodboard(tenant=current_user.id, **mb.model_dump())
    db.add(db_mb)
    db.commit(); db.refresh(db_mb)
    return db_mb

@router.get("/moodboards", response_model=List[MoodboardResponse])
async def list_moodboards(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    return db.query(Moodboard).filter(Moodboard.tenant == current_user.id).all()

# --- PHOTO JOURNAL ---
@router.post("/photo-journals", response_model=PhotoJournalResponse)
async def create_photo_entry(entry: PhotoJournalCreate, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    db_entry = PhotoJournal(tenant=current_user.id, **entry.model_dump())
    db.add(db_entry)
    db.commit(); db.refresh(db_entry)
    return db_entry

@router.get("/photo-journals", response_model=List[PhotoJournalResponse])
async def list_photo_entries(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    return db.query(PhotoJournal).filter(PhotoJournal.tenant == current_user.id).order_by(PhotoJournal.date.desc()).all()

# --- NUDGES ---
@router.get("/nudges", response_model=List[NudgeResponse])
async def list_nudges(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    return db.query(Nudge).filter(Nudge.tenant == current_user.id, Nudge.is_read == False).all()

# --- QUIZZES ---
@router.post("/quizzes", response_model=QuizResponse)
async def create_quiz(quiz: QuizCreate, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    # Assuming user can create quizzes
    db_quiz = Quiz(created_by=current_user.id, **quiz.model_dump())
    db.add(db_quiz)
    db.commit(); db.refresh(db_quiz)
    return db_quiz

@router.get("/quizzes", response_model=List[QuizResponse])
async def list_quizzes(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    # Return system quizzes + user created quizzes
    return db.query(Quiz).filter((Quiz.created_by == current_user.id) | (Quiz.is_system == True)).all()
