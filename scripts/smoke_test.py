import os
import requests

def main():
    host = os.getenv('ELINITY_HOST', 'http://localhost:8080')
    try:
        r = requests.get(f"{host}/health", timeout=5)
        print('GET /health ->', r.status_code, r.text)
    except Exception as e:
        print('Error contacting /health:', e)

if __name__ == '__main__':
    main()
