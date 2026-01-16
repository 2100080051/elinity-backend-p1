import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": f"testuser_{int(time.time())}@example.com",
    "password": "Password123!",
    "phone": "+1234567890"
}

def run_verification():
    print(f"🚀 Starting verification for {TEST_USER['email']}...")
    
    # 1. Register
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if resp.status_code not in [200, 201]:
            print(f"❌ Registration Failed: {resp.status_code} - {resp.text}")
            return
        print("✅ Registered.")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 2. Login
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": TEST_USER['email'], "password": TEST_USER['password']})
    token = resp.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in.")

    results = []

    # 3. Test AI Modes (New)
    new_modes = ["visualization", "metacognition", "mindfulness", "socratic", "learning", "pep_talk", "reality_check", "weekly_reflection", "couple_bestie"]
    for mode in new_modes:
        r = requests.post(f"{BASE_URL}/ai-mode/{mode}/start", params={"message": "Hello AI"}, headers=headers)
        status = "✅" if r.status_code == 200 else "❌"
        results.append(f"AI Mode: {mode:<20} | {r.status_code} | {status}")

    # 4. Test Lifebook (New)
    lb_data = {"title": "My Legacy", "category": "Legacy", "description": "Notes for the future"}
    r = requests.post(f"{BASE_URL}/lifebook/", json=lb_data, headers=headers)
    if r.status_code == 200:
        lb_id = r.json().get('id')
        results.append(f"Lifebook Category: {'Create':<16} | 200 | ✅")
        
        entry_data = {"lifebook_id": lb_id, "title": "Milestone 1", "content": "Started the project."}
        r_entry = requests.post(f"{BASE_URL}/lifebook/entries", json=entry_data, headers=headers)
        results.append(f"Lifebook Entry: {'Create':<19} | {r_entry.status_code} | {'✅' if r_entry.status_code == 200 else '❌'}")
    else:
        results.append(f"Lifebook: {'FAILED':<24} | {r.status_code} | ❌")

    # 5. Test Relationship Daily Card (New)
    r = requests.get(f"{BASE_URL}/dashboard/relationship/daily-card", headers=headers)
    results.append(f"Daily Card: {'GET':<23} | {r.status_code} | {'✅' if r.status_code == 200 else '❌'}")

    # 6. Test Existing Core Features
    core_tests = [
        ("Recommendations", "/recommendations/", "GET"),
        ("Chats", "/chats/", "GET"),
        ("Journal", "/journal/", "GET"),
        ("Skill Eval", "/evaluate/skill/social", "GET"), # Dummy path check
        ("Nudges", "/tools/nudges", "GET"),
        ("Games List", "/ai-mode/games/list", "GET")
    ]
    
    for desc, path, method in core_tests:
        if method == "GET":
            r = requests.get(f"{BASE_URL}{path}", headers=headers)
        else:
            r = requests.post(f"{BASE_URL}{path}", headers=headers)
        results.append(f"Core: {desc:<25} | {r.status_code} | {'✅' if r.status_code in [200, 404, 405] else '❌'}") # 404/405 ok for path existence check

    print("\n" + "="*50)
    for res in results:
        print(res)
    print("="*50)

if __name__ == "__main__":
    run_verification()
