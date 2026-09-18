import requests
import time
import sys

try:
    print("Testing backend connectivity on :8000")
    b_res = requests.get("http://localhost:8000/api/health", timeout=3)
    if b_res.status_code == 200:
        print("Backend: OK -", b_res.json())
    else:
        print("Backend: Failed, status code", b_res.status_code)
        sys.exit(1)

    print("Testing Live Monitor interface API")
    i_res = requests.get("http://localhost:8000/api/live/interfaces", timeout=15)
    if i_res.status_code == 200:
        print("Live Interfaces: OK -", len(i_res.json().get('interfaces', [])), "interfaces found")
    else:
        print("Live Interfaces: Failed, status code", i_res.status_code)
        sys.exit(1)

except Exception as e:
    print("Verification Error:", e)
    sys.exit(1)

print("All Verification Passed!")
