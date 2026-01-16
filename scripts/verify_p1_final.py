import requests
import json
import time

BASE_URL = "http://localhost:8081" # Local docker port
USER_PHONE = "+19998887778"
REGISTER_DATA = {
    "phone": USER_PHONE,
    "password": "password123",
    "personal_info": {
        "first_name": "Verification",
        "last_name": "User",
        "location": "New York",
        "relationship_status": "Single"
    },
    "interests_and_hobbies": {
        "interests": ["Philosophy", "Meditation", "AI", "Startup", "Dating"]
    }
}

def log(msg):
    print(f"\n>>> {msg}")
    with open("FINAL_VERIFICATION_REPORT.txt", "a", encoding="utf-8") as f:
        f.write(f"\n\n>>> {msg}\n")

def test_endpoint(name, method, path, data=None, params=None, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"{BASE_URL}{path}"
    try:
        if method == "POST":
            resp = requests.post(url, json=data, params=params, headers=headers, timeout=60)
        else:
            resp = requests.get(url, params=params, headers=headers, timeout=60)
        
        status = resp.status_code
        result = resp.json() if resp.status_code < 500 else resp.text
        log(f"{name} | Status: {status}")
        with open("FINAL_VERIFICATION_REPORT.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(result, indent=2))
        return result
    except Exception as e:
        log(f"{name} | Error: {str(e)}")
        return None

def main():
    with open("FINAL_VERIFICATION_REPORT.txt", "w", encoding="utf-8") as f:
        f.write("ELINITY P1 FINAL VERIFICATION REPORT\n")
        f.write("====================================\n")

    log("Step 1: User Registration & Login")
    reg = test_endpoint("Register", "POST", "/auth/register", data=REGISTER_DATA)
    login = test_endpoint("Login", "POST", "/auth/login", data={"phone": USER_PHONE, "password": "password123"})
    
    token = login.get("access_token") if login else None
    if not token:
        log("CRITICAL: Login failed, cannot proceed.")
        return

    log("Step 2: Testing Specialized Experience Modes")
    modes = ["meditation", "visualization", "deep_thinking", "learning", "pep_talk", "reality_check", "reflection"]
    for m in modes:
        test_endpoint(f"Mode: {m}", "POST", f"/ai-mode/{m}/start", data={"message": "I want to start a session."}, token=token)

    log("Step 3: Testing Character Personas")
    personas = ["tough_love", "empathetic", "sassy", "wise_elder", "hype", "zen", "philosopher", "oracle"]
    for p in personas:
        test_endpoint(f"Persona: {p}", "POST", f"/ai-mode/{p}/start", data={"message": "I've been procrastinating lately."}, token=token)

    log("Step 4: Testing Historical Personas")
    historical = ["jung", "socrates_historical", "musashi", "aurelius"]
    for h in historical:
        test_endpoint(f"Historical: {h}", "POST", f"/ai-mode/{h}/start", data={"message": "What is the meaning of life?"}, token=token)

    log("Step 5: Testing Specialized Matching & Recommendations")
    matching_queries = [
        ("Romantic Match", "Find me a romantic partner who loves deep philosophy."),
        ("Friendship Match", "I want to find friends to play connection games with."),
        ("Work Match", "Looking for a co-founder for an AI startup.")
    ]
    for name, q in matching_queries:
        test_endpoint(name, "GET", "/recommendations/search", params={"query": q}, token=token)

    log("Step 6: Testing Icebreakers & Vibe Checks")
    test_endpoint("Icebreaker (Universal)", "POST", "/chats/icebreaker", params={"mode": "universal"}, token=token)
    test_endpoint("Vibe Check (Personality)", "POST", "/chats/vibe-check", params={"type": "personality"}, token=token)

    log("Step 7: Testing Smart Journal (Multimodal)")
    test_endpoint("Smart Journal", "POST", "/multimodal/process/", data={"url": "https://example.com/audio.mp3"}, token=token)

    log("Step 8: Testing Relationship Suite & Dashboard")
    test_endpoint("Relationship Dashboard", "GET", "/dashboard/relationship", token=token)
    test_endpoint("Daily Relationship Card", "GET", "/dashboard/relationship/daily-card", token=token)

    log("Step 9: Testing Lifebook")
    lb = test_endpoint("Create Lifebook Category", "POST", "/lifebook/", data={"title": "My Visions", "category": "Visions", "description": "Goals for 2026"}, token=token)
    if lb and "id" in lb:
        test_endpoint("Add Lifebook Entry", "POST", "/lifebook/entries", data={"lifebook_id": lb["id"], "title": "AI OS Vision", "content": "I want to build an AI OS.", "media_urls": ["https://example.com/vision.jpg"]}, token=token)

    log("Step 10: Testing Connection Games")
    test_endpoint("List Games", "GET", "/ai-mode/games/list", token=token)
    test_endpoint("Recommend Game", "POST", "/ai-mode/games/recommend", params={"query": "We want something fun and deep for a first date."}, token=token)

    log("Step 11: Testing Messaging & Interaction")
    # Using a fake target ID (the one we created or a seeded one)
    target_id = "007aa51a-5b8d-4255-8d97-0c95ef81c563" 
    test_endpoint("Send Direct Message", "POST", f"/chats/direct/{target_id}", data={"message": "Hey! I saw we have a high match for philosophy."}, token=token)

    log("Step 12: Testing Nudges & Rituals")
    test_endpoint("Create Ritual", "POST", "/tools/rituals", data={"title": "Daily Reflection", "description": "10 minutes of journaling", "frequency": "daily"}, token=token)
    test_endpoint("Verify Dashboard with Rituals", "GET", "/dashboard/relationship", token=token)

    log("VERIFICATION COMPLETE. All outputs saved to FINAL_VERIFICATION_REPORT.txt")

if __name__ == "__main__":
    main()
