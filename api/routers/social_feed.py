from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from models.user import Tenant
from models.social import SocialPost, SocialInteraction
from schemas.social import SocialPostCreate, SocialPostResponse
from utils.token import get_current_user

router = APIRouter(tags=["Social Feed"])

@router.get("/", response_model=List[SocialPostResponse])
async def get_feed(db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Get social feed. Currently returns all posts (Public Feed MVP)."""
    # In a real expanded app, we'd filter by friends.
    posts = db.query(SocialPost).order_by(SocialPost.created_at.desc()).limit(50).all()
    return posts

@router.post("/", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: SocialPostCreate, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Create a new social post."""
    db_post = SocialPost(author_id=current_user.id, **post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.post("/{post_id}/like", response_model=SocialPostResponse)
async def like_post(post_id: str, db: Session = Depends(get_db), current_user: Tenant = Depends(get_current_user)):
    """Like a post."""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if already liked
    if current_user.id not in post.likes:
        # Add to post.likes JSON
        new_likes = list(post.likes)
        new_likes.append(current_user.id)
        post.likes = new_likes
        
        # Log interaction
        interaction = SocialInteraction(
            user_id=current_user.id,
            target_id=post_id,
            target_type="post",
            interaction_type="like"
        )
        db.add(interaction)
        
        db.commit()
        db.refresh(post)
        
    return post
