import requests, base64, os, json

api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/chat/completions"

payload = {
    "model": "nvidia/nemotron-nano-12b-v2-vl:free",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Describe this video."},
    ]
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://example.com",
    "X-Title": "Nemotron Test",
    "Content-Type": "application/json",
}

r = requests.post(url, json=payload, headers=headers)

# 👇 Add this to debug full response
print("Raw response:\n", r.text)

try:
    data = r.json()
    if "choices" in data:
        print("\nAI Output:\n", data["choices"][0]["message"]["content"])
    elif "error" in data:
        print("\n❌ API Error:\n", data["error"]["message"])
    else:
        print("\n⚠️ Unexpected response format.")
except Exception as e:
    print("❌ Could not parse response:", e)
