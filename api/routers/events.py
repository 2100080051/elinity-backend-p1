from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.user import Tenant
from models.social import Event
from schemas.social import EventCreate, EventResponse
from utils.token import get_current_user

router = APIRouter(tags=["Events"])

@router.get("/", response_model=List[EventResponse])
async def list_events(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """List events where the user is host or attendee."""
    # Simple logic: get events hosted by user. 
    # Expanded logic would query JSON `attendees` but that can be slow in SQL.
    # For MVP, we return events hosted by user.
    events = db.query(Event).filter(Event.host_id == current_user.id).all()
    return events

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Create a new event."""
    db_event = Event(host_id=current_user.id, **event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.post("/{event_id}/invite", response_model=EventResponse)
async def invite_user(event_id: str, user_id: str, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Invite a user to an event."""
    event = db.query(Event).filter(Event.id == event_id, Event.host_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    current_attendees = list(event.attendees)
    if user_id not in current_attendees:
        current_attendees.append(user_id)
        # Re-assign to trigger SQLAlchemy detection of JSON change
        event.attendees = current_attendees 
        db.commit()
        db.refresh(event)
    
    return event
