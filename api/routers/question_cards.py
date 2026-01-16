from fastapi import APIRouter,Depends
from schemas.question_cards import QuestionCardQuery, QuestionCard
from typing import List
from utils.token import get_current_user
from models.user import Tenant
from database.session import get_db,Session
from sqlalchemy.orm import selectinload
from schemas.user import User
import random

router = APIRouter()


@router.get("/cards/",tags=["Question Cards"],response_model=List[QuestionCard])
def generate_cards(query: QuestionCardQuery = Depends(),current_user: Tenant = Depends(get_current_user),db: Session = Depends(get_db)):
    # Predefined "Deep Persona" Question Cards (Static List)
    # Designed for introspection and connection without heavy AI generation
    STATIC_CARDS = [
        {"text": "What is the most significant change you've made in your life recently?", "category": "Growth", "color": "#FF6B6B", "tags": ["growth", "change"]},
        {"text": "If you could have a conversation with your younger self, what determines the topic?", "category": "Self", "color": "#4ECDC4", "tags": ["self", "reflection"]},
        {"text": "What is a value you hold that you will never compromise on?", "category": "Values", "color": "#FFE66D", "tags": ["values", "integrity"]},
        {"text": "Who in your life brings out the best in you, and how?", "category": "Social", "color": "#1A535C", "tags": ["friends", "relationship"]},
        {"text": "What does your ideal day of rest look like?", "category": "Lifestyle", "color": "#F7FFF7", "tags": ["rest", "lifestyle"]},
        {"text": "What is a skill you are currently trying to master?", "category": "Growth", "color": "#FF6B6B", "tags": ["learning"]},
        {"text": "Describe a moment when you felt truly at peace.", "category": "Self", "color": "#4ECDC4", "tags": ["peace", "emotion"]},
        {"text": "What is one fear you are actively working to overcome?", "category": "Growth", "color": "#FF6B6B", "tags": ["fear", "courage"]},
        {"text": "If you could live anywhere for a year, where would it be?", "category": "Dreams", "color": "#FFE66D", "tags": ["travel", "dreams"]},
        {"text": "What helps you recharge when you are feeling drained?", "category": "Lifestyle", "color": "#F7FFF7", "tags": ["energy", "self-care"]},
        {"text": "What is the kindest thing someone has done for you recently?", "category": "Social", "color": "#1A535C", "tags": ["kindness", "gratitude"]},
        {"text": "What is a book, movie, or song that changed your perspective?", "category": "Inspiration", "color": "#FF6B6B", "tags": ["art", "inspiration"]},
        {"text": "How do you define success for yourself right now?", "category": "Values", "color": "#FFE66D", "tags": ["success", "definition"]},
        {"text": "What is a childhood memory that still makes you smile?", "category": "Memory", "color": "#4ECDC4", "tags": ["childhood", "joy"]},
        {"text": "What are you most grateful for today?", "category": "Self", "color": "#F7FFF7", "tags": ["gratitude"]}
    ]
    
    # Select random cards from pool
    selected_data = random.sample(STATIC_CARDS, min(query.count, len(STATIC_CARDS)))
    
    return [QuestionCard(**c) for c in selected_data]

# ---------------------------
# [NEW] Answer Persistence
# ---------------------------
from schemas.question_cards import QuestionCardAnswerCreate, QuestionCardAnswerResponse
from models.question_card import QuestionCardAnswer

@router.post("/answers/", tags=["Question Cards"], response_model=QuestionCardAnswerResponse)
async def save_answer(
    payload: QuestionCardAnswerCreate,
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a user's answer to a specific question card."""
    answer_obj = QuestionCardAnswer(
        tenant_id=current_user.id,
        card_content=payload.card_content,
        answer=payload.answer
    )
    db.add(answer_obj)
    db.commit()
    db.refresh(answer_obj)
    return answer_obj

@router.get("/answers/", tags=["Question Cards"], response_model=List[QuestionCardAnswerResponse])
async def get_answers(
    current_user: Tenant = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history of answered cards."""
    return db.query(QuestionCardAnswer).filter(
        QuestionCardAnswer.tenant_id == current_user.id
    ).order_by(QuestionCardAnswer.created_at.desc()).all()

