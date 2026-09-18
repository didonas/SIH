import requests
import time

time.sleep(2) # wait for boot
try:
    res = requests.get("http://localhost:8000/api/live/interfaces")
    ifaces = res.json().get('interfaces', [])
    print("Interfaces:", ifaces)
    
    if ifaces:
        start_res = requests.post("http://localhost:8000/api/live/start", json={"interface": ifaces[0]})
        print("Start res:", start_res.json())
        
        time.sleep(3)
        status_res = requests.get("http://localhost:8000/api/live/status")
        print("Status:", status_res.json())
        
        stop_res = requests.post("http://localhost:8000/api/live/stop")
        print("Stop res:", stop_res.json())
        
except Exception as e:
    print("API Error:", e)
