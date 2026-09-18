import requests
import time

# Give the frontend a few seconds to boot
time.sleep(3)

print("Checking Frontend on :5174...")
try:
    r = requests.get('http://localhost:5174/')
    if r.status_code == 200:
        print("Frontend Root: OK")
    else:
        print(f"Frontend Root: FAILED ({r.status_code})")
        
    r = requests.get('http://localhost:5174/monitor')
    if r.status_code == 200:
        print("Frontend Monitor: OK")
    else:
        print(f"Frontend Monitor: FAILED ({r.status_code})")
except Exception as e:
    print(f"Frontend: FAILED ({e})")
