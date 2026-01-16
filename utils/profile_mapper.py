from typing import Dict, Any, Optional
from database.session import Session
from models.user import Tenant, PersonalInfo, InterestsAndHobbies, RelationshipPreferences, ValuesBeliefsAndGoals
import logging

logger = logging.getLogger("profile_mapper")


def upsert_personal_info(db: Session, tenant_id: str, data: Dict[str, Any]):
    pi = db.query(PersonalInfo).filter(PersonalInfo.tenant == tenant_id).first()
    if not pi:
        pi = PersonalInfo(tenant=tenant_id)
        db.add(pi)

    # Only update fields that are present and non-empty
    for f in ['first_name','middle_name','last_name','age','gender','sexual_orientation','location','relationship_status','education','occupation','profile_pictures']:
        if f in data and data.get(f) is not None:
            setattr(pi, f, data.get(f))

    db.commit(); db.refresh(pi)
    return pi


def upsert_interests_hobbies(db: Session, tenant_id: str, data: Dict[str, Any]):
    ih = db.query(InterestsAndHobbies).filter(InterestsAndHobbies.tenant == tenant_id).first()
    if not ih:
        ih = InterestsAndHobbies(tenant=tenant_id)
        db.add(ih)

    if 'interests' in data and data.get('interests') is not None:
        ih.interests = data.get('interests')
    if 'hobbies' in data and data.get('hobbies') is not None:
        ih.hobbies = data.get('hobbies')

    db.commit(); db.refresh(ih)
    return ih


def upsert_relationship_preferences(db: Session, tenant_id: str, data: Dict[str, Any]):
    rp = db.query(RelationshipPreferences).filter(RelationshipPreferences.tenant == tenant_id).first()
    if not rp:
        rp = RelationshipPreferences(tenant=tenant_id)
        db.add(rp)

    if 'seeking' in data and data.get('seeking') is not None:
        rp.seeking = data.get('seeking')
    if 'looking_for' in data and data.get('looking_for') is not None:
        rp.looking_for = data.get('looking_for')
    if 'relationship_goals' in data and data.get('relationship_goals') is not None:
        rp.relationship_goals = data.get('relationship_goals')
    if 'dealbreakers' in data and data.get('dealbreakers') is not None:
        rp.deal_breakers = data.get('dealbreakers')
    if 'what_i_offer' in data and data.get('what_i_offer') is not None:
        rp.what_i_offer = data.get('what_i_offer')

    db.commit(); db.refresh(rp)
    return rp


def upsert_values_goals(db: Session, tenant_id: str, data: Dict[str, Any]):
    vg = db.query(ValuesBeliefsAndGoals).filter(ValuesBeliefsAndGoals.tenant == tenant_id).first()
    if not vg:
        vg = ValuesBeliefsAndGoals(tenant=tenant_id)
        db.add(vg)

    if 'values' in data and data.get('values') is not None:
        vg.values = data.get('values')
    if 'beliefs' in data and data.get('beliefs') is not None:
        vg.beliefs = data.get('beliefs')
    if 'personal_goals' in data and data.get('personal_goals') is not None:
        vg.personal_goals = data.get('personal_goals')
    if 'professional_goals' in data and data.get('professional_goals') is not None:
        vg.professional_goals = data.get('professional_goals')

    db.commit(); db.refresh(vg)
    return vg


def persist_profile(db: Session, tenant_id: str, profile: Dict[str, Any]):
    """Persist allowed parts of the generated profile into related tables.

    This is intentionally conservative: only writes fields that are present and non-null.
    """
    results = {}
    try:
        if 'personal_info' in profile and profile.get('personal_info'):
            results['personal_info'] = upsert_personal_info(db, tenant_id, profile.get('personal_info'))

        if 'interests_and_hobbies' in profile and profile.get('interests_and_hobbies'):
            results['interests_and_hobbies'] = upsert_interests_hobbies(db, tenant_id, profile.get('interests_and_hobbies'))

        if 'relationship_preferences' in profile and profile.get('relationship_preferences'):
            results['relationship_preferences'] = upsert_relationship_preferences(db, tenant_id, profile.get('relationship_preferences'))

        if 'values_beliefs_and_goals' in profile and profile.get('values_beliefs_and_goals'):
            results['values_beliefs_and_goals'] = upsert_values_goals(db, tenant_id, profile.get('values_beliefs_and_goals'))

        return results
    except Exception as e:
        logger.exception("Failed to persist profile")
        db.rollback()
        raise
