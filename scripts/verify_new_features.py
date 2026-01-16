import requests
import json

BASE_URL = "http://localhost:8000"
EMAIL = "emma.wilson@test.com"
PASSWORD = "Emma123!@#"

def test_new_features():
    print("🚀 Starting Verification of New Features...")
    
    # 1. Login
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"❌ Login Failed: {resp.status_code}")
            return
        token = resp.json().get('access_token')
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 2. Test AI Modes
    modes = ["visualization", "metacognition", "mindfulness", "socratic", "pep_talk", "reality_check"]
    for mode in modes:
        print(f"🔍 Testing AI Mode: {mode}...")
        resp = requests.post(f"{BASE_URL}/ai-mode/{mode}/start", 
                             params={"message": "I want to start a session."}, 
                             headers=headers)
        if resp.status_code == 200:
            print(f"✅ {mode} output: {resp.json().get('ai_message')[:100]}...")
        else:
            print(f"❌ {mode} failed: {resp.status_code}")

    # 3. Test Lifebook
    print("🔍 Testing Lifebook creation...")
    lb_data = {
        "title": "My Health Vision",
        "category": "Health",
        "description": "Visualizing my healthy future.",
        "content": {"goals": ["Run a marathon", "Eat clean"]}
    }
    resp = requests.post(f"{BASE_URL}/lifebook/", json=lb_data, headers=headers)
    if resp.status_code == 200:
        lb_id = resp.json().get('id')
        print(f"✅ Lifebook created: {lb_id}")
        
        # Add Entry
        entry_data = {
            "lifebook_id": lb_id,
            "title": "First Step",
            "content": "Bought new running shoes today!"
        }
        resp = requests.post(f"{BASE_URL}/lifebook/entries", json=entry_data, headers=headers)
        if resp.status_code == 200:
            print("✅ Lifebook entry created.")
    else:
        print(f"❌ Lifebook failed: {resp.status_code}")

    # 4. Test Daily Card
    print("🔍 Testing Relationship Daily Card...")
    resp = requests.get(f"{BASE_URL}/dashboard/relationship/daily-card", headers=headers)
    if resp.status_code == 200:
        print(f"✅ Daily Card: {resp.json().get('daily_card').get('insight')}")
    else:
        print(f"❌ Daily Card failed: {resp.status_code}")

if __name__ == "__main__":
    test_new_features()
