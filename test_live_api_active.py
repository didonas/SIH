import requests
import time
import urllib.request
import threading

time.sleep(2) # wait for boot
target = r"\Device\NPF_{7659D7F9-95E7-47CA-888E-4F1E2E8859D6}"
try:
    start_res = requests.post("http://localhost:8000/api/live/start", json={"interface": target})
    print("Start res:", start_res.json())
    
    def generate_traffic():
        try:
            urllib.request.urlopen("http://example.com", timeout=2)
            urllib.request.urlopen("http://example.org", timeout=2)
        except:
            pass
            
    t = threading.Thread(target=generate_traffic)
    t.start()
    
    time.sleep(3)
    status_res = requests.get("http://localhost:8000/api/live/status")
    print("Status:", status_res.json())
    
    stop_res = requests.post("http://localhost:8000/api/live/stop")
    print("Stop res:", stop_res.json())
    
except Exception as e:
    print("API Error:", e)
