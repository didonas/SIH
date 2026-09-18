import requests
import sys
try:
    print("Testing backend connectivity...")
    b_res = requests.get("http://localhost:8000/api/health", timeout=3)
    print("Health:", b_res.json())
    
    print("Testing Live Interfaces...")
    i_res = requests.get("http://localhost:8000/api/live/interfaces", timeout=5)
    print("Interfaces:", [i['display'] for i in i_res.json().get('interfaces', [])])
except Exception as e:
    print("Error:", e)
    sys.exit(1)
