import requests
import time
import urllib.request
import threading

time.sleep(2) # wait for boot
try:
    ifaces_res = requests.get("http://localhost:8000/api/live/interfaces").json()
    ifaces = ifaces_res.get('interfaces', [])
    target = None
    for i in ifaces:
        if "10.214.224.222" in i["display"]:
            target = i["id"]
            break
            
    if not target:
        target = ifaces[0]["id"]
        print("Fallback to first interface")
        
    print(f"Target interface selected: {target}")
    
    start_res = requests.post("http://localhost:8000/api/live/start", json={"interface": target})
    print("Start res:", start_res.json())
    
    def generate_traffic():
        try:
            for _ in range(5):
                urllib.request.urlopen("http://example.com", timeout=2)
                time.sleep(0.5)
        except Exception as e:
            pass
            
    t = threading.Thread(target=generate_traffic)
    t.start()
    
    time.sleep(6) # Let the 5-sec buffer window flush
    status_res = requests.get("http://localhost:8000/api/live/status")
    print("Status:", status_res.json())
    
    stop_res = requests.post("http://localhost:8000/api/live/stop")
    print("Stop res:", stop_res.json())
    
except Exception as e:
    print("API Error:", e)
