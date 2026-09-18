import requests
import time
import os
import threading
import sys

time.sleep(2) # wait for boot
try:
    print("--- 1. Testing Live Capture (Normal Traffic on Loopback) ---")
    ifaces_res = requests.get("http://localhost:8000/api/live/interfaces").json()
    ifaces = ifaces_res.get('interfaces', [])
    target = None
    for i in ifaces:
        if "Loopback" in i["display"] or "127.0.0.1" in i["display"]:
            target = i["id"]
            break
            
    requests.post("http://localhost:8000/api/live/start", json={"interface": target})
    
    def generate_traffic():
        try:
            for _ in range(5):
                os.system("ping 127.0.0.1 -n 4 > nul")
                time.sleep(0.5)
        except Exception as e:
            pass
            
    t = threading.Thread(target=generate_traffic)
    t.start()
    
    time.sleep(8)
    status_res = requests.get("http://localhost:8000/api/live/status").json()
    requests.post("http://localhost:8000/api/live/stop")
    
    flood_alerts = [a for a in status_res.get('recent_alerts', []) if 'FLOOD' in a['threat_type']]
    if len(flood_alerts) > 0:
        print(f"FAIL: Live capture generated FLOOD alerts on normal traffic!")
        sys.exit(1)
    else:
        print("PASS: Normal traffic triggered 0 FLOOD alerts.")
        
    print("\n--- 2. Testing SYN Flood PCAP ---")
    with open('test_traffic/syn_flood/syn_flood.pcap', 'rb') as f:
        res = requests.post("http://localhost:8000/api/analyze/pcap", files={'file': f})
        data = res.json()
        alerts = data.get('alerts', [])
        types = set(a['threat_type'] for a in alerts)
        print("SYN Flood Alert Types:", types)
        if any('FLOOD' in t for t in types):
            print("PASS: SYN Flood properly detected.")
        else:
            print("FAIL: SYN Flood not detected as flood!")
            
    print("\n--- 3. Testing Port Scan PCAP ---")
    with open('test_traffic/port_scan/port_scan.pcap', 'rb') as f:
        res = requests.post("http://localhost:8000/api/analyze/pcap", files={'file': f})
        data = res.json()
        alerts = data.get('alerts', [])
        types = set(a['threat_type'] for a in alerts)
        print("Port Scan Alert Types:", types)
        if any('SCAN' in t or 'RECON' in t for t in types):
            print("PASS: Port Scan properly detected.")
        else:
            print("FAIL: Port Scan not detected!")

except Exception as e:
    print("Test Error:", e)
