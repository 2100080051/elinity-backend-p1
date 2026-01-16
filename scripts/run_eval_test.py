import os
import asyncio
import json

# Force safe environment: empty OPENROUTER_API_KEY to avoid external API calls
os.environ.pop('OPENROUTER_API_KEY', None)
# Force DB failure by pointing DB_HOST to an invalid host
os.environ['DB_HOST'] = 'invalid-host-for-test'

from api.routers.skill_evaluation import evaluate_direct

async def run_test():
    payload = {
        "skill_title": "Active Listening",
        "skill_description": "Practice listening without interrupting.",
        "session_type": "text",
        "transcript": "USER: I feel ignored. ASSISTANT: I hear you. Tell me more. USER: I often get cut off."
    }
    try:
        result = await evaluate_direct(payload)
    except Exception as e:
        result = {"error": str(e)}

    os.makedirs('results', exist_ok=True)
    with open('results/eval_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print('Test complete. Result written to results/eval_test_result.json')

if __name__ == '__main__':
    asyncio.run(run_test())
