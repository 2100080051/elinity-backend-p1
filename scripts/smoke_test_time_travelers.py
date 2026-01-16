from fastapi.testclient import TestClient
import sys
from pathlib import Path
import json

# Ensure project root is on sys.path so `import main` works when this script
# is run from the scripts/ directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
import main

client = TestClient(main.app)

print('== START: Time Travelers smoke test ==')
resp = client.post('/games/time-travelers/start_journey', json={'players': ['Alice','Bob']})
print('start_journey ->', resp.status_code)
try:
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print('failed to parse json:', e)

session = resp.json().get('session')
first_era = resp.json().get('first_era')

resp2 = client.post('/games/time-travelers/player_respond', json={
    'session': session,
    'player_name': 'Alice',
    'response': 'I pull out a strange device and press a red button',
    'current_era': first_era
})
print('\nplayer_respond ->', resp2.status_code)
print(json.dumps(resp2.json(), indent=2))

resp3 = client.post('/games/time-travelers/next_jump', json={
    'session': session,
    'jump_count': 1,
    'previous_era': first_era
})
print('\nnext_jump ->', resp3.status_code)
print(json.dumps(resp3.json(), indent=2))

resp4 = client.post('/games/time-travelers/end_journey', json={
    'session': session,
    'total_jumps': 2
})
print('\nend_journey ->', resp4.status_code)
print(json.dumps(resp4.json(), indent=2))

print('== END: Time Travelers smoke test ==')
