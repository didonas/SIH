import requests
import time
import os
import threading
import sys
import urllib.request

time.sleep(2) # wait for boot
try:
    print("--- 1. Testing Live Capture Resolution Logic ---")
    ifaces_res = requests.get("http://localhost:8000/api/live/interfaces").json()
    ifaces = ifaces_res.get('interfaces', [])
    target_display = None
    for i in ifaces:
        if "10.214.224.222" in i["display"] or "Remote NDIS" in i["display"]:
            target_display = i["display"]
            break
            
    if not target_display:
        print("Could not find Ethernet 4. Falling back to Loopback for test logic verification.")
        for i in ifaces:
            if "Loopback" in i["display"] or "127.0.0.1" in i["display"]:
                target_display = i["display"]
                break
                
    if not target_display:
        target_display = ifaces[0]["display"]
        
    print(f"Target stable friendly name selected: '{target_display}'")
    
    start_res = requests.post("http://localhost:8000/api/live/start", json={"interface": target_display})
    print("Start res:", start_res.json())
    
    def generate_traffic():
        try:
            if "Loopback" in target_display:
                for _ in range(5):
                    os.system("ping 127.0.0.1 -n 4 > nul")
                    time.sleep(0.5)
            else:
                for _ in range(5):
                    urllib.request.urlopen("http://example.com", timeout=2)
                    time.sleep(0.5)
        except Exception as e:
            pass
            
    t = threading.Thread(target=generate_traffic)
    t.start()
    
    time.sleep(10) # Let the 5-sec buffer window flush
    status_res = requests.get("http://localhost:8000/api/live/status").json()
    requests.post("http://localhost:8000/api/live/stop")
    
    print("Live Traffic Status:", status_res)
    
    if status_res.get('status') == 'ERROR':
        print(f"FAIL: Capture threw error: {status_res.get('error')}")
        sys.exit(1)
        
    if status_res.get('packets_observed', 0) == 0:
        print("FAIL: No packets observed on resolved interface.")
        sys.exit(1)
    else:
        print(f"PASS: Capture successfully resolved stable name and captured {status_res['packets_observed']} packets!")

except Exception as e:
    print("Test Error:", e)
