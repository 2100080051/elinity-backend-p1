import requests
import json
import time

import os
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8081")
USER_DEFAULT = {"email": "tester_report@test.com", "password": "Password123!", "phone": "+1999888777"}

def get_output(desc, method, path, payload=None, params=None, headers=None, timeout=30):
    try:
        # Avoid double slashes but ensure leading slash
        full_path = path if path.startswith("/") else "/" + path
        url = f"{BASE_URL}{full_path}"
        
        if method == "GET":
            r = requests.get(url, headers=headers, params=params, timeout=timeout)
        else:
            r = requests.post(url, headers=headers, json=payload, params=params, timeout=timeout)
        
        status = r.status_code
        try:
            data = r.json()
        except:
            data = r.text
        return {"feature": desc, "status": status, "output": data}
    except Exception as e:
        return {"feature": desc, "status": "ERROR", "output": str(e)}

def generate_report():
    print("Preparing fresh user for final run...")
    # Unique suffix to avoid "already exists" errors
    suffix = str(int(time.time()))[-5:]
    user = {
        "email": f"final_tester_{suffix}@test.com", 
        "password": "Password123!", 
        "phone": f"+100{suffix}"
    }
    
    try:
        # Register
        requests.post(f"{BASE_URL}/auth/register", json=user)
        # Login
        r = requests.post(f"{BASE_URL}/auth/login", json={"email": user["email"], "password": user["password"]})
        token = r.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Logged in as {user['email']}")
    except Exception as e:
        print(f"Setup failed: {e}")
        return

    results = []
    
    # 1. Recommendation & Matching (Longer timeout)
    print("Verifying Recommendations...")
    results.append(get_output("Matching/Recommendations", "GET", "/recommendations/", headers=headers, timeout=60))
    
    # 2. Messaging & AI Chat Analysis
    print("Verifying Messaging...")
    results.append(get_output("Messaging List", "GET", "/chats/", headers=headers))
    
    # 3. Prompt-based Features
    print("Verifying AI Modes...")
    modes = [
        "coach", "therapist", "meditation", "visualization", "metacognition", 
        "mindfulness", "socratic", "learning", "pep_talk", "reality_check", 
        "weekly_reflection", "couple_bestie"
    ]
    for mode in modes:
        results.append(get_output(f"AI Mode: {mode}", "POST", f"/ai-mode/{mode}/start", 
                                  params={"message": "Begin session."}, headers=headers, timeout=45))

    # 4. Skill Learning Sessions (Fixed paths)
    print("Verifying Skills...")
    results.append(get_output("Skill: Relationship", "GET", "/relationship-skills/", headers=headers))
    results.append(get_output("Skill: Self-Growth", "GET", "/self-growth/", headers=headers))
    results.append(get_output("Skill: Social", "GET", "/social/", headers=headers))
    
    # 5. Lifebook
    print("Verifying Lifebook...")
    results.append(get_output("Lifebook Categories", "GET", "/lifebook/", headers=headers))
    
    # 6. Voice Smart Journal
    print("Verifying Voice Journal...")
    # Try different slash combinations if 404 persists
    results.append(get_output("Voice/Multimodal Journal", "POST", "/multimodal/process/", 
                              payload={"url": "https://example.com/audio.wav"}, headers=headers))
    
    # 7. Connection Games
    print("Verifying Games...")
    results.append(get_output("Connection Games List", "GET", "/ai-mode/games/list", headers=headers))
    
    # 8. Relationship Suite
    print("Verifying Relationship Suite...")
    results.append(get_output("Relationship Hub", "GET", "/dashboard/relationship", headers=headers))
    results.append(get_output("Daily Relationship Card", "GET", "/dashboard/relationship/daily-card", headers=headers))
    results.append(get_output("Streaks", "GET", "/tools/rituals", headers=headers))
    results.append(get_output("Nudges", "GET", "/tools/nudges", headers=headers))

    # Final Summary
    with open("FINAL_CORE_OUTPUTS.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nFINAL STATUS SUMMARY\n" + "="*40)
    for res in results:
        status_icon = "✅" if res['status'] == 200 else "❌"
        print(f"{status_icon} {res['feature']:<25} | Status: {res['status']}")
    print("="*40)

if __name__ == "__main__":
    generate_report()
