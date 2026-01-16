from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class PersonalInfoSchema(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    sexual_orientation: Optional[str] = None
    location: Optional[str] = None
    relationship_status: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    profile_pictures: Optional[List[str]] = []


class InterestsAndHobbiesSchema(BaseModel):
    interests: Optional[List[str]] = []
    hobbies: Optional[List[str]] = []


class RelationshipPreferencesSchema(BaseModel):
    seeking: Optional[str] = None
    looking_for: Optional[List[str]] = []
    relationship_goals: Optional[str] = None
    dealbreakers: Optional[List[str]] = []
    what_i_offer: Optional[List[str]] = []


class ValuesBeliefsAndGoalsSchema(BaseModel):
    values: Optional[List[str]] = []
    beliefs: Optional[str] = None
    personal_goals: Optional[List[str]] = []
    professional_goals: Optional[List[str]] = []


class GeneratedProfileSchema(BaseModel):
    personal_info: Optional[PersonalInfoSchema] = None
    interests_and_hobbies: Optional[InterestsAndHobbiesSchema] = None
    relationship_preferences: Optional[RelationshipPreferencesSchema] = None
    values_beliefs_and_goals: Optional[ValuesBeliefsAndGoalsSchema] = None
    # allow extra unknown fields
    other: Optional[Dict[str, Any]] = None
