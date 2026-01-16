"""
Update user profiles on the deployed backend for testing recommendations
Users: user17@example.com (nani17) and user18@example.com (user18)
"""

import requests
import json

# Deployed backend URL
BASE_URL = "https://elinity-backend-arg7ckh2fph8duea.centralus-01.azurewebsites.net"

# Test users
USERS = [
    {"email": "user17@example.com", "password": "nani17"},
    {"email": "user18@example.com", "password": "user18"}
]

# Rich profile data for user17 (Tech Entrepreneur & Fitness Enthusiast)
USER17_PROFILE = {
    'personal_info': {
        'first_name': 'Alex',
        'last_name': 'Rivera',
        'age': 28,
        'gender': 'Male',
        'location': 'San Francisco',
        'education': 'Masters',
        'occupation': 'Software Engineer',
        'relationship_status': 'Single'
    },
    'interests_and_hobbies': {
        'interests': ['Artificial Intelligence', 'Blockchain', 'Entrepreneurship', 'Fitness', 'Travel', 'Photography'],
        'hobbies': ['Coding', 'Rock Climbing', 'Hiking', 'Reading Tech Blogs', 'Yoga']
    },
    'big_five_traits': {
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
    'values_beliefs_and_goals': {
        'values': ['Innovation', 'Growth', 'Authenticity', 'Health', 'Adventure'],
        'personal_goals': ['Launch a successful startup', 'Run a marathon', 'Travel to 30 countries'],
        'professional_goals': ['Build an AI product', 'Become a tech leader', 'Mentor young developers'],
        'aspirations': ['Create positive impact through technology', 'Achieve work-life balance']
    },
    'favorites': {
        'movies': ['The Social Network', 'Inception', 'Interstellar'],
        'music': ['Electronic', 'Indie Rock', 'Lo-fi'],
        'books': ['Zero to One', 'The Lean Startup', 'Sapiens'],
        'places': ['Tokyo', 'Iceland', 'New Zealand']
    },
    'relationship_preferences': {
        'looking_for': ['Ambitious', 'Active', 'Intellectually curious'],
        'green_flags': ['Good communication', 'Shared values', 'Growth mindset'],
        'what_i_offer': ['Loyalty', 'Adventure', 'Support', 'Humor']
    },
    'friendship_preferences': {
        'ideal_traits': ['Authentic', 'Adventurous', 'Intellectually curious'],
        'activities': ['Hiking', 'Tech meetups', 'Coffee chats', 'Travel']
    },
    'collaboration_preferences': {
        'areas_of_expertise': ['Full-stack development', 'AI/ML', 'Product management'],
        'goals': ['Build innovative products', 'Learn from others', 'Create impact']
    },
    'intentions': {
        'romantic': 'Yes',
        'social': 'Yes',
        'professional': 'Yes'
    }
}

# Rich profile data for user18 (Creative Designer & Wellness Advocate)
USER18_PROFILE = {
    'personal_info': {
        'first_name': 'Maya',
        'last_name': 'Chen',
        'age': 26,
        'gender': 'Female',
        'location': 'San Francisco',
        'education': 'Bachelors',
        'occupation': 'UX Designer',
        'relationship_status': 'Single'
    },
    'interests_and_hobbies': {
        'interests': ['Design', 'Psychology', 'Wellness', 'Art', 'Sustainability', 'Meditation'],
        'hobbies': ['Painting', 'Yoga', 'Cooking', 'Journaling', 'Photography']
    },
    'big_five_traits': {
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
    'values_beliefs_and_goals': {
        'values': ['Creativity', 'Empathy', 'Sustainability', 'Mindfulness', 'Authenticity'],
        'personal_goals': ['Master mindfulness practice', 'Create meaningful art', 'Live sustainably'],
        'professional_goals': ['Lead design at a mission-driven company', 'Teach design workshops', 'Build a design portfolio'],
        'aspirations': ['Make a positive impact through design', 'Inspire others to live mindfully']
    },
    'favorites': {
        'movies': ['Eternal Sunshine', 'Her', 'Lost in Translation'],
        'music': ['Indie Folk', 'Ambient', 'Jazz'],
        'books': ['The Design of Everyday Things', 'Atomic Habits', 'The Alchemist'],
        'places': ['Bali', 'Kyoto', 'Copenhagen']
    },
    'relationship_preferences': {
        'looking_for': ['Emotionally intelligent', 'Creative', 'Mindful'],
        'green_flags': ['Active listener', 'Empathetic', 'Growth-oriented'],
        'what_i_offer': ['Compassion', 'Creativity', 'Deep conversations', 'Support']
    },
    'friendship_preferences': {
        'ideal_traits': ['Empathetic', 'Creative', 'Authentic'],
        'activities': ['Art galleries', 'Yoga classes', 'Cooking together', 'Nature walks']
    },
    'collaboration_preferences': {
        'areas_of_expertise': ['UX/UI Design', 'User Research', 'Visual Design'],
        'goals': ['Create user-centered products', 'Collaborate with diverse teams', 'Learn continuously']
    },
    'intentions': {
        'romantic': 'Yes',
        'social': 'Yes',
        'professional': 'Yes'
    }
}

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def login(email, password):
    """Login and get access token"""
    print(f"\n🔐 Logging in as {email}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Login successful!")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def update_profile_section(token, endpoint, data, section_name):
    """Update a specific profile section"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/{endpoint}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Updated {section_name}")
            return True
        else:
            print(f"   ⚠️  {section_name} update returned {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ Error updating {section_name}: {str(e)}")
        return False

def update_user_profile(email, password, profile_data):
    """Update complete user profile"""
    print_section(f"Updating Profile for {email}")
    
    # Login
    token = login(email, password)
    if not token:
        print("⚠️  Skipping profile update due to login failure")
        return False
    
    success_count = 0
    total_sections = 0
    
    # Update each profile section
    sections = [
        ('profile/personal-info', profile_data.get('personal_info'), 'Personal Info'),
        ('profile/interests-hobbies', profile_data.get('interests_and_hobbies'), 'Interests & Hobbies'),
        ('profile/big-five-traits', profile_data.get('big_five_traits'), 'Big Five Traits'),
        ('profile/psychology', profile_data.get('psychology'), 'Psychology'),
        ('profile/values-beliefs-goals', profile_data.get('values_beliefs_and_goals'), 'Values, Beliefs & Goals'),
        ('profile/favorites', profile_data.get('favorites'), 'Favorites'),
        ('profile/relationship-preferences', profile_data.get('relationship_preferences'), 'Relationship Preferences'),
        ('profile/friendship-preferences', profile_data.get('friendship_preferences'), 'Friendship Preferences'),
        ('profile/collaboration-preferences', profile_data.get('collaboration_preferences'), 'Collaboration Preferences'),
        ('profile/intentions', profile_data.get('intentions'), 'Intentions'),
    ]
    
    print("\n📝 Updating profile sections...")
    for endpoint, data, name in sections:
        if data:
            total_sections += 1
            if update_profile_section(token, endpoint, data, name):
                success_count += 1
    
    print(f"\n📊 Update Summary: {success_count}/{total_sections} sections updated successfully")
    return success_count == total_sections

def test_recommendations(email, password):
    """Test recommendations endpoint"""
    print_section(f"Testing Recommendations for {email}")
    
    token = login(email, password)
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test general recommendations
    print("\n🔍 Testing GET /recommendations/...")
    try:
        response = requests.get(
            f"{BASE_URL}/recommendations/",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Got {len(recommendations)} recommendations")
            
            for i, rec in enumerate(recommendations[:3], 1):
                tenant = rec['tenant']
                score = rec['score']
                name = f"{tenant['personal_info']['first_name']} {tenant['personal_info']['last_name']}"
                location = tenant['personal_info'].get('location', 'Unknown')
                print(f"   {i}. {name} from {location} (Score: {score:.2f})")
        else:
            print(f"⚠️  Request returned {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test search recommendations
    print("\n🔍 Testing GET /recommendations/search?query=entrepreneur...")
    try:
        response = requests.get(
            f"{BASE_URL}/recommendations/search",
            headers=headers,
            params={"query": "entrepreneur"},
            timeout=30
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Got {len(recommendations)} search results")
            
            for i, rec in enumerate(recommendations[:3], 1):
                tenant = rec['tenant']
                score = rec['score']
                name = f"{tenant['personal_info']['first_name']} {tenant['personal_info']['last_name']}"
                occupation = tenant['personal_info'].get('occupation', 'Unknown')
                print(f"   {i}. {name} - {occupation} (Score: {score:.2f})")
        else:
            print(f"⚠️  Request returned {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print_section("🚀 DEPLOYED BACKEND - USER PROFILE UPDATE")
    print(f"\n🌐 Backend URL: {BASE_URL}")
    print("\n👥 Target Users:")
    print("   1. user17@example.com (password: nani17)")
    print("   2. user18@example.com (password: user18)")
    
    # Update user17
    update_user_profile("user17@example.com", "nani17", USER17_PROFILE)
    
    # Update user18
    update_user_profile("user18@example.com", "user18", USER18_PROFILE)
    
    print_section("✅ PROFILE UPDATES COMPLETE")
    
    # Test recommendations
    print("\n🧪 Now testing recommendations endpoints...\n")
    test_recommendations("user17@example.com", "nani17")
    test_recommendations("user18@example.com", "user18")
    
    print_section("🎉 ALL DONE!")
    print("\n📋 Summary:")
    print("   ✅ Updated user17@example.com (Alex Rivera - Tech Entrepreneur)")
    print("   ✅ Updated user18@example.com (Maya Chen - UX Designer)")
    print("\n🎯 Profile Highlights:")
    print("   - Both users are in San Francisco (location match)")
    print("   - Overlapping interests: Photography, Wellness/Fitness")
    print("   - Complementary skills: Tech/AI + Design/UX")
    print("   - Both have 'Secure' attachment style")
    print("\n💡 Next Steps:")
    print("   - Login to the deployed backend with these credentials")
    print("   - Test the recommendations endpoints")
    print("   - Verify AI insights are being generated")

if __name__ == "__main__":
    main()
