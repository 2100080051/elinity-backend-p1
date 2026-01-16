from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.user import Tenant
from models.lifebook import Lifebook, LifebookEntry
from schemas.lifebook import (
    LifebookCreate, LifebookResponse,
    LifebookEntryCreate, LifebookEntryResponse
)
from utils.token import get_current_user

router = APIRouter(prefix="", tags=["Lifebook"])

@router.post("/", response_model=LifebookResponse)
async def create_lifebook_category(
    lb: LifebookCreate, 
    db: Session = Depends(get_db), 
    current_user: Tenant = Depends(get_current_user)
):
    db_lb = Lifebook(tenant=current_user.id, **lb.model_dump())
    db.add(db_lb)
    db.commit()
    db.refresh(db_lb)
    return db_lb

@router.get("/", response_model=List[LifebookResponse])
async def list_lifebook_categories(
    db: Session = Depends(get_db), 
    current_user: Tenant = Depends(get_current_user)
):
    return db.query(Lifebook).filter(Lifebook.tenant == current_user.id).all()

@router.post("/entries", response_model=LifebookEntryResponse)
async def create_lifebook_entry(
    entry: LifebookEntryCreate, 
    db: Session = Depends(get_db), 
    current_user: Tenant = Depends(get_current_user)
):
    # Verify lifebook category belongs to user
    category = db.query(Lifebook).filter(
        Lifebook.id == entry.lifebook_id, 
        Lifebook.tenant == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Lifebook category not found")
        
    db_entry = LifebookEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/{lifebook_id}/entries", response_model=List[LifebookEntryResponse])
async def list_lifebook_entries(
    lifebook_id: str, 
    db: Session = Depends(get_db), 
    current_user: Tenant = Depends(get_current_user)
):
    # Verify access
    category = db.query(Lifebook).filter(
        Lifebook.id == lifebook_id, 
        Lifebook.tenant == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Lifebook category not found")
        
    return db.query(LifebookEntry).filter(LifebookEntry.lifebook_id == lifebook_id).all()
