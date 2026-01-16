import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from passlib.hash import bcrypt as _bcrypt
from database.session import Session
from models.user import (
    Tenant, ProfilePicture, PersonalInfo, BigFiveTraits, MBTITraits, Psychology,
    InterestsAndHobbies, ValuesBeliefsAndGoals, Favorites,
    RelationshipPreferences, FriendshipPreferences,
    CollaborationPreferences, PersonalFreeForm, Intentions,
    IdealCharacteristics, AspirationAndReflections, Lifestyle, KeyMemories
)

session = Session()

def update_or_create_user(email, password, profile_data):
    """Update or create a user with rich profile data"""
    
    # Check if user exists
    user = session.query(Tenant).filter(Tenant.email == email).first()
    
    if not user:
        # Create new user
        print(f"Creating new user: {email}")
        user = Tenant(
            email=email,
            password=_bcrypt.hash(password),
            role='user'
        )
        session.add(user)
        session.flush()
    else:
        print(f"Updating existing user: {email}")
        # Update password
        user.password = _bcrypt.hash(password)
    
    # Update or create PersonalInfo
    if user.personal_info:
        personal = user.personal_info
    else:
        personal = PersonalInfo(tenant=user.id)
        session.add(personal)
    
    personal.first_name = profile_data['first_name']
    personal.last_name = profile_data['last_name']
    personal.age = profile_data['age']
    personal.gender = profile_data['gender']
    personal.location = profile_data['location']
    personal.education = profile_data['education']
    personal.occupation = profile_data['occupation']
    personal.relationship_status = profile_data.get('relationship_status', 'Single')
    
    # Update or create InterestsAndHobbies
    if user.interests_and_hobbies:
        interests = user.interests_and_hobbies
    else:
        interests = InterestsAndHobbies(tenant=user.id)
        session.add(interests)
    
    interests.interests = profile_data['interests']
    interests.hobbies = profile_data['hobbies']
    
    # Update or create BigFiveTraits
    if user.big_five_traits:
        traits = user.big_five_traits
    else:
        traits = BigFiveTraits(tenant=user.id)
        session.add(traits)
    
    traits.openness = profile_data['traits']['openness']
    traits.conscientiousness = profile_data['traits']['conscientiousness']
    traits.extraversion = profile_data['traits']['extraversion']
    traits.agreeableness = profile_data['traits']['agreeableness']
    traits.neuroticism = profile_data['traits']['neuroticism']
    
    # Update or create Psychology
    if user.psychology:
        psychology = user.psychology
    else:
        psychology = Psychology(tenant=user.id)
        session.add(psychology)
    
    psychology.attachment_style = profile_data['psychology']['attachment_style']
    psychology.emotional_intelligence = profile_data['psychology']['emotional_intelligence']
    psychology.cognitive_style = profile_data['psychology']['cognitive_style']
    psychology.stress_tolerance = profile_data['psychology']['stress_tolerance']
    psychology.conflict_resolution_style = profile_data['psychology']['conflict_resolution_style']
    
    # Update or create ValuesBeliefsAndGoals
    if user.values_beliefs_and_goals:
        values = user.values_beliefs_and_goals
    else:
        values = ValuesBeliefsAndGoals(tenant=user.id)
        session.add(values)
    
    values.values = profile_data['values']
    values.personal_goals = profile_data['personal_goals']
    values.professional_goals = profile_data['professional_goals']
    values.aspirations = profile_data.get('aspirations', [])
    
    # Update or create Favorites
    if user.favorites:
        favorites = user.favorites
    else:
        favorites = Favorites(tenant=user.id)
        session.add(favorites)
    
    favorites.movies = profile_data['favorites']['movies']
    favorites.music = profile_data['favorites']['music']
    favorites.books = profile_data['favorites']['books']
    favorites.places = profile_data['favorites']['places']
    
    # Update or create RelationshipPreferences
    if user.relationship_preferences:
        rel_pref = user.relationship_preferences
    else:
        rel_pref = RelationshipPreferences(tenant=user.id)
        session.add(rel_pref)
    
    rel_pref.looking_for = profile_data['relationship_prefs']['looking_for']
    rel_pref.green_flags = profile_data['relationship_prefs']['green_flags']
    rel_pref.what_i_offer = profile_data['relationship_prefs']['what_i_offer']
    
    # Update or create FriendshipPreferences
    if user.friendship_preferences:
        friend_pref = user.friendship_preferences
    else:
        friend_pref = FriendshipPreferences(tenant=user.id)
        session.add(friend_pref)
    
    friend_pref.ideal_traits = profile_data['friendship_prefs']['ideal_traits']
    friend_pref.activities = profile_data['friendship_prefs']['activities']
    
    # Update or create CollaborationPreferences
    if user.collaboration_preferences:
        collab_pref = user.collaboration_preferences
    else:
        collab_pref = CollaborationPreferences(tenant=user.id)
        session.add(collab_pref)
    
    collab_pref.areas_of_expertise = profile_data['collaboration_prefs']['areas_of_expertise']
    collab_pref.goals = profile_data['collaboration_prefs']['goals']
    
    # Update or create Intentions
    if user.intentions:
        intentions = user.intentions
    else:
        intentions = Intentions(tenant=user.id)
        session.add(intentions)
    
    intentions.romantic = profile_data['intentions']['romantic']
    intentions.social = profile_data['intentions']['social']
    intentions.professional = profile_data['intentions']['professional']
    
    session.commit()
    print(f"✅ Successfully updated {email}")
    return user


# User 19 Profile - Tech Entrepreneur & Fitness Enthusiast
user19_data = {
    'first_name': 'Alex',
    'last_name': 'Rivera',
    'age': 28,
    'gender': 'Male',
    'location': 'San Francisco',
    'education': 'Masters',
    'occupation': 'Software Engineer',
    'relationship_status': 'Single',
    'interests': ['Artificial Intelligence', 'Blockchain', 'Entrepreneurship', 'Fitness', 'Travel', 'Photography'],
    'hobbies': ['Coding', 'Rock Climbing', 'Hiking', 'Reading Tech Blogs', 'Yoga'],
    'traits': {
        'openness': 0.85,
        'conscientiousness': 0.78,
        'extraversion': 0.72,
        'agreeableness': 0.80,
        'neuroticism': 0.35
    },
    'psychology': {
        'attachment_style': 'Secure',
        'emotional_intelligence': 0.82,
        'cognitive_style': 'Analytical',
        'stress_tolerance': 'High',
        'conflict_resolution_style': 'Collaborative'
    },
    'values': ['Innovation', 'Growth', 'Authenticity', 'Health', 'Adventure'],
    'personal_goals': ['Launch a successful startup', 'Run a marathon', 'Travel to 30 countries'],
    'professional_goals': ['Build an AI product', 'Become a tech leader', 'Mentor young developers'],
    'aspirations': ['Create positive impact through technology', 'Achieve work-life balance'],
    'favorites': {
        'movies': ['The Social Network', 'Inception', 'Interstellar'],
        'music': ['Electronic', 'Indie Rock', 'Lo-fi'],
        'books': ['Zero to One', 'The Lean Startup', 'Sapiens'],
        'places': ['Tokyo', 'Iceland', 'New Zealand']
    },
    'relationship_prefs': {
        'looking_for': ['Ambitious', 'Active', 'Intellectually curious'],
        'green_flags': ['Good communication', 'Shared values', 'Growth mindset'],
        'what_i_offer': ['Loyalty', 'Adventure', 'Support', 'Humor']
    },
    'friendship_prefs': {
        'ideal_traits': ['Authentic', 'Adventurous', 'Intellectually curious'],
        'activities': ['Hiking', 'Tech meetups', 'Coffee chats', 'Travel']
    },
    'collaboration_prefs': {
        'areas_of_expertise': ['Full-stack development', 'AI/ML', 'Product management'],
        'goals': ['Build innovative products', 'Learn from others', 'Create impact']
    },
    'intentions': {
        'romantic': 'Yes',
        'social': 'Yes',
        'professional': 'Yes'
    }
}

# User 13 Profile - Creative Designer & Wellness Advocate
user13_data = {
    'first_name': 'Maya',
    'last_name': 'Chen',
    'age': 26,
    'gender': 'Female',
    'location': 'San Francisco',
    'education': 'Bachelors',
    'occupation': 'UX Designer',
    'relationship_status': 'Single',
    'interests': ['Design', 'Psychology', 'Wellness', 'Art', 'Sustainability', 'Meditation'],
    'hobbies': ['Painting', 'Yoga', 'Cooking', 'Journaling', 'Photography'],
    'traits': {
        'openness': 0.90,
        'conscientiousness': 0.75,
        'extraversion': 0.65,
        'agreeableness': 0.88,
        'neuroticism': 0.40
    },
    'psychology': {
        'attachment_style': 'Secure',
        'emotional_intelligence': 0.88,
        'cognitive_style': 'Creative',
        'stress_tolerance': 'Medium',
        'conflict_resolution_style': 'Compromising'
    },
    'values': ['Creativity', 'Empathy', 'Sustainability', 'Mindfulness', 'Authenticity'],
    'personal_goals': ['Master mindfulness practice', 'Create meaningful art', 'Live sustainably'],
    'professional_goals': ['Lead design at a mission-driven company', 'Teach design workshops', 'Build a design portfolio'],
    'aspirations': ['Make a positive impact through design', 'Inspire others to live mindfully'],
    'favorites': {
        'movies': ['Eternal Sunshine', 'Her', 'Lost in Translation'],
        'music': ['Indie Folk', 'Ambient', 'Jazz'],
        'books': ['The Design of Everyday Things', 'Atomic Habits', 'The Alchemist'],
        'places': ['Bali', 'Kyoto', 'Copenhagen']
    },
    'relationship_prefs': {
        'looking_for': ['Emotionally intelligent', 'Creative', 'Mindful'],
        'green_flags': ['Active listener', 'Empathetic', 'Growth-oriented'],
        'what_i_offer': ['Compassion', 'Creativity', 'Deep conversations', 'Support']
    },
    'friendship_prefs': {
        'ideal_traits': ['Empathetic', 'Creative', 'Authentic'],
        'activities': ['Art galleries', 'Yoga classes', 'Cooking together', 'Nature walks']
    },
    'collaboration_prefs': {
        'areas_of_expertise': ['UX/UI Design', 'User Research', 'Visual Design'],
        'goals': ['Create user-centered products', 'Collaborate with diverse teams', 'Learn continuously']
    },
    'intentions': {
        'romantic': 'Yes',
        'social': 'Yes',
        'professional': 'Yes'
    }
}

if __name__ == "__main__":
    print("🔄 Updating test users for recommendations testing...\n")
    
    # Update user19@example.com
    update_or_create_user('user19@example.com', 'user19', user19_data)
    
    # Update user13@example.com
    update_or_create_user('user13@example.com', 'user13', user13_data)
    
    print("\n✅ All test users updated successfully!")
    print("\n📝 Test User Credentials:")
    print("   User 1: user19@example.com / user19")
    print("   User 2: user13@example.com / user13")
    print("\n🎯 These users now have rich profiles for testing recommendations!")
    print("   - Both are in San Francisco (location match)")
    print("   - Overlapping interests: Photography, Wellness/Fitness")
    print("   - Complementary traits: Alex (Tech/Analytical) + Maya (Design/Creative)")
    print("   - Both have 'Secure' attachment style and high emotional intelligence")
    
    session.close()
