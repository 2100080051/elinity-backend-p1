import requests
import json
import time

BASE_URL = "http://localhost:8000"
USER = {
    "email": f"test_{int(time.time())}@test.com", 
    "password": "Password123!", 
    "phone": f"+1{int(time.time())}"
}

def verify():
    with open("verify_results.txt", "w") as f:
        f.write("Starting Final Verification...\n")
        try:
            reg = requests.post(f"{BASE_URL}/auth/register", json=USER)
            f.write(f"Register: {reg.status_code}\n")
            
            # Use a known existing user if registration failed (for local testing continuity)
            login_data = {"email": USER["email"], "password": USER["password"]}
            r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if r.status_code != 200:
                 # Fallback to seeded user if local DB is already populated
                 r = requests.post(f"{BASE_URL}/auth/login", json={"email": "emma.wilson@test.com", "password": "Emma123!@#"})
            
            token = r.json().get("access_token")
            if not token:
                f.write("Login: FAILED (No token)\n")
                return
            
            headers = {"Authorization": f"Bearer {token}"}
            f.write("Login: OK\n")
            
            # AI Modes
            modes = ["visualization", "metacognition", "mindfulness", "socratic", "learning", "pep_talk", "reality_check", "weekly_reflection", "couple_bestie"]
            for m in modes:
                resp = requests.post(f"{BASE_URL}/ai-mode/{m}/start", params={"message": "start"}, headers=headers)
                f.write(f"AI Mode {m}: {resp.status_code}\n")
                if resp.status_code == 200:
                    f.write(f"  Output preview: {resp.json().get('ai_message')[:50]}...\n")

            # Lifebook
            r = requests.post(f"{BASE_URL}/lifebook/", json={"title": "Test", "category": "Health"}, headers=headers)
            f.write(f"Lifebook: {r.status_code}\n")
            
            # Daily Card
            r = requests.get(f"{BASE_URL}/dashboard/relationship/daily-card", headers=headers)
            f.write(f"Daily Card: {r.status_code}\n")
            if r.status_code == 200:
                  f.write(f"  Insight: {r.json().get('daily_card', {}).get('insight')}\n")
            
            f.write("All tests completed!\n")
        except Exception as e:
            f.write(f"Error: {str(e)}\n")

if __name__ == "__main__":
    verify()
