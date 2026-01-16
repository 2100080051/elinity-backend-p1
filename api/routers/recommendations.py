import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from elinity_ai.milvus_db import MilvusUserSimilarityPipeline
from models.user import Tenant
from schemas.user import RecommendedUserSchema, TenantSchema
from database.session import get_db
from utils.token import get_current_user
from elinity_ai.milvus_db import milvus_db
router = APIRouter()

# Lazy-load insights to avoid import-time failures when langchain/Google credentials are missing
_insights = None


def get_insights():
    global _insights
    if _insights is not None:
        return _insights
    try:
        from elinity_ai.insights import ElinityInsights
        _insights = ElinityInsights()
    except Exception:
        # If dependencies are missing, fall back to a stub that returns a simple string
        def _fallback_insight(query: str, user_id: str, user_name: str, score: float, user_interests: str):
            return f"Insights unavailable (missing deps/creds); score={score:.2f}"

        class _Fallback:
            def generate_insight(self, query, user_id, user_name, score, user_interests=""):
                return _fallback_insight(query, user_id, user_name, score, user_interests)

        _insights = _Fallback()
    return _insights

def process_tenant_insight(tenant: Tenant, query: str, score: float) -> RecommendedUserSchema:
    """Helper function to process one tenant and get AI insight."""
    user_name = "Unknown User"
    try:
        insights = get_insights()
        user_id = tenant.id
        name_parts = [
            tenant.personal_info.first_name,
            tenant.personal_info.middle_name,
            tenant.personal_info.last_name
        ]
        user_name = " ".join(part for part in name_parts if part) or "Unknown User"
        
        user_interests = ','.join(tenant.interests_and_hobbies.interests or [])

        # SYNC execution (safe in threadpool)
        ai_insight_text = insights.generate_insight(
            query=query,
            user_id=user_id,
            user_name=user_name,
            score=score,
            user_interests=user_interests
        )

        return RecommendedUserSchema(
            tenant=TenantSchema.model_validate(tenant),
            score=score,
            ai_insight=ai_insight_text
        )
    except Exception as e:
        print(f"Error processing insight for user {tenant.id}: {e}")
        return RecommendedUserSchema(
            tenant=TenantSchema.model_validate(tenant),
            score=score,
            ai_insight=f"Could not generate insight for {user_name}."
        )


@router.get("/search", tags=["Recommendations"], response_model=List[RecommendedUserSchema])
def get_recommendations_optimized(
    query: str, 
    current_user: Tenant = Depends(get_current_user), 
    db: Session = Depends(get_db)
): 
    try:
        # 1. Fetch Candidates (up to 50 active users)
        # Executing synchronously (FastAPI threadpool)
        candidates = db.query(Tenant).filter(
            Tenant.id != current_user.id
        ).limit(50).all()
        
        # 2. Calculate Similarity Score (Python Logic)
        try:
            # Accessing relationships triggers lazy loads (safe in sync)
            my_interests = set(current_user.interests_and_hobbies.interests or []) if current_user.interests_and_hobbies else set()
            my_location = current_user.personal_info.location.lower() if current_user.personal_info and current_user.personal_info.location else ""
        except Exception as e:
            print(f"Error accessing current user profile: {e}")
            my_interests = set()
            my_location = ""
    
        scored_candidates = []
        
        for user in candidates:
            try:
                score = 0.1 # Base score for being on the platform
                
                # Interest Overlap (Lazy load safe in sync)
                their_interests = set(user.interests_and_hobbies.interests or []) if user.interests_and_hobbies else set()
                overlap = len(my_interests.intersection(their_interests))
                if overlap > 0:
                    score += min(overlap * 0.2, 0.5) # Cap at 0.5
                    
                # Location Match
                their_location = user.personal_info.location.lower() if user.personal_info and user.personal_info.location else ""
                if my_location and their_location and my_location == their_location:
                    score += 0.3
                    
                scored_candidates.append({"user": user, "score": score})
            except Exception as e:
                 # print(f"Skipping candidate {user.id} due to error: {e}") 
                 continue
    
        # 3. Sort by Score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        top_matches = scored_candidates[:5]
    
        # 4. Generate AI Insights & Response (Sequential Sync)
        users_with_insights = []
        for item in top_matches:
            tenant = item["user"]
            score = item["score"]
            # Pass empty query string as this is general recommendation
            # Function is now sync, returns object directly
            result = process_tenant_insight(tenant, query, score)
            users_with_insights.append(result)
    
        users_with_insights.sort(key=lambda x: x.score, reverse=True)
    
        return users_with_insights
    
    except Exception as e:
        print(f"DEBUG: Query Failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Recommendation Error: {str(e)}")


@router.get("/", tags=["Recommendations"])
async def get_recommendations(current_user: Tenant = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get recommendations for the current user"""

    # 4. Query database for similar users
    # 5. Return list of recommended users
    # HEURISTIC RECOMMENDATION ENGINE (Replacing Mock/Milvus)
    # 1. Fetch Candidates (up to 50 active users)
    print("DEBUG: Executing Recommendation Query...")
    try:
        candidates = db.query(Tenant).filter(
            Tenant.id != current_user.id
        ).limit(50).all()
        print(f"DEBUG: Query success. Found {len(candidates)} candidates.")
    except Exception as e:
        print(f"DEBUG: Query Failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB Error: {str(e)}")
        
    # 2. Calculate Similarity Score (Python Logic)
    try:
        # Accessing relationships might trigger lazy loads
        my_interests = set(current_user.interests_and_hobbies.interests or []) if current_user.interests_and_hobbies else set()
        my_location = current_user.personal_info.location.lower() if current_user.personal_info and current_user.personal_info.location else ""
    except Exception as e:
        print(f"Error accessing current user profile: {e}")
        my_interests = set()
        my_location = ""

    scored_candidates = []
    
    for user in candidates:
        try:
            score = 0.1 # Base score for being on the platform
            
            # Interest Overlap
            their_interests = set(user.interests_and_hobbies.interests or []) if user.interests_and_hobbies else set()
            overlap = len(my_interests.intersection(their_interests))
            if overlap > 0:
                score += min(overlap * 0.2, 0.5) # Cap at 0.5
                
            # Location Match
            their_location = user.personal_info.location.lower() if user.personal_info and user.personal_info.location else ""
            if my_location and their_location and my_location == their_location:
                score += 0.3
                
            scored_candidates.append({"user": user, "score": score})
        except Exception as e:
             print(f"Skipping candidate {user.id} due to error: {e}")
             continue

    # 3. Sort by Score
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    top_matches = scored_candidates[:5]

    # 4. Generate AI Insights & Response (Sequential Sync)
    users_with_insights = []
    for item in top_matches:
        tenant = item["user"]
        score = item["score"]
        # Pass empty query string as this is general recommendation
        # Function is now sync, returns object directly
        result = process_tenant_insight(tenant, "", score)
        users_with_insights.append(result)

    users_with_insights.sort(key=lambda x: x.score, reverse=True)

    return users_with_insights 
 