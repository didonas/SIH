import requests
import time

time.sleep(4)

print("Checking Frontend on :5175...")
try:
    r = requests.get('http://localhost:5175/')
    if r.status_code == 200:
        if "SOC IDS" in r.text or "SIH" in r.text or "Threat Detection" in r.text:
            print("Frontend Root: OK (Contains SOC IDS or related terms)")
        else:
            print("Frontend Root: OK (But missing expected title, text length:", len(r.text), ")")
    else:
        print(f"Frontend Root: FAILED ({r.status_code})")
except Exception as e:
    print(f"Frontend: FAILED ({e})")
