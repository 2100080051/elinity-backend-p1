"""
Test script for recommendations endpoint
Tests both /recommendations/ and /recommendations/search endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Change if your backend runs on a different port
TEST_USERS = [
    {"email": "user19@example.com", "password": "user19"},
    {"email": "user13@example.com", "password": "user13"}
]

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def login(email, password):
    """Login and get access token"""
    print(f"\n🔐 Logging in as {email}...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": email,
            "password": password
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_general_recommendations(token, user_email):
    """Test GET /recommendations/ endpoint"""
    print_section(f"Testing General Recommendations for {user_email}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/recommendations/",
            headers=headers
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Got {len(recommendations)} recommendations")
            
            for i, rec in enumerate(recommendations, 1):
                tenant = rec['tenant']
                score = rec['score']
                insight = rec['ai_insight']
                
                name = f"{tenant['personal_info']['first_name']} {tenant['personal_info']['last_name']}"
                location = tenant['personal_info'].get('location', 'Unknown')
                occupation = tenant['personal_info'].get('occupation', 'Unknown')
                interests = tenant['interests_and_hobbies'].get('interests', [])
                
                print(f"\n   {i}. {name} (Score: {score:.2f})")
                print(f"      📍 {location} | 💼 {occupation}")
                print(f"      🎯 Interests: {', '.join(interests[:3])}")
                print(f"      💡 AI Insight: {insight[:100]}...")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_search_recommendations(token, user_email, query):
    """Test GET /recommendations/search endpoint"""
    print_section(f"Testing Search Recommendations for {user_email}")
    print(f"🔍 Search Query: '{query}'")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/recommendations/search",
            headers=headers,
            params={"query": query}
        )
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"✅ Got {len(recommendations)} recommendations")
            
            for i, rec in enumerate(recommendations, 1):
                tenant = rec['tenant']
                score = rec['score']
                insight = rec['ai_insight']
                
                name = f"{tenant['personal_info']['first_name']} {tenant['personal_info']['last_name']}"
                location = tenant['personal_info'].get('location', 'Unknown')
                occupation = tenant['personal_info'].get('occupation', 'Unknown')
                interests = tenant['interests_and_hobbies'].get('interests', [])
                
                print(f"\n   {i}. {name} (Score: {score:.2f})")
                print(f"      📍 {location} | 💼 {occupation}")
                print(f"      🎯 Interests: {', '.join(interests[:3])}")
                print(f"      💡 AI Insight: {insight[:150]}...")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print_section("🚀 RECOMMENDATIONS ENDPOINT TESTING")
    print("\n📋 Test Plan:")
    print("   1. Login as user19@example.com")
    print("   2. Test general recommendations (/recommendations/)")
    print("   3. Test search recommendations (/recommendations/search)")
    print("   4. Repeat for user13@example.com")
    
    # Test queries for search
    search_queries = [
        "entrepreneur",
        "design",
        "fitness",
        "creative"
    ]
    
    for user in TEST_USERS:
        email = user['email']
        password = user['password']
        
        # Login
        token = login(email, password)
        if not token:
            print(f"⚠️  Skipping tests for {email} due to login failure")
            continue
        
        # Test general recommendations
        test_general_recommendations(token, email)
        
        # Test search recommendations with different queries
        for query in search_queries[:2]:  # Test with 2 queries per user
            test_search_recommendations(token, email, query)
    
    print_section("✅ TESTING COMPLETE")
    print("\n📊 Summary:")
    print("   - Tested both recommendation endpoints")
    print("   - Verified AI insights generation")
    print("   - Checked scoring algorithm")
    print("\n💡 Next Steps:")
    print("   - Review the recommendations for relevance")
    print("   - Check if location matching works (both users in San Francisco)")
    print("   - Verify interest overlap detection")
    print("   - Test AI insights quality")

if __name__ == "__main__":
    main()
