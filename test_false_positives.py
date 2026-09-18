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
            
    if not target:
        print("Could not find loopback adapter.")
        sys.exit(1)
        
    print(f"Target interface selected: {target}")
    
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
    
    time.sleep(12) # Let the 5-sec buffer window flush twice
    status_res = requests.get("http://localhost:8000/api/live/status").json()
    requests.post("http://localhost:8000/api/live/stop")
    
    print("Normal Live Traffic Status:", status_res)
    
    flood_alerts = [a for a in status_res.get('recent_alerts', []) if 'FLOOD' in a['threat_type']]
    if status_res['packets_observed'] == 0:
        print("FAIL: No packets observed on loopback.")
        sys.exit(1)
    elif len(flood_alerts) > 0:
        print(f"FAIL: Live capture generated FLOOD alerts on normal traffic!")
        print("Alerts:", flood_alerts)
        sys.exit(1)
    else:
        print("PASS: Normal traffic triggered 0 FLOOD alerts.")
        
    print("\n--- 2. Testing SYN Flood PCAP ---")
    with open('test_traffic/syn_flood/syn_flood.pcap', 'rb') as f:
        res = requests.post("http://localhost:8000/api/analyze/pcap", files={'file': f})
        data = res.json()
        print("SYN Flood Alerts:", data['threats_found'])
        if data['threats_found'] > 0:
            print("PASS: SYN Flood detected.")
        else:
            print("FAIL: SYN Flood not detected!")
            sys.exit(1)
            
    print("\n--- 3. Testing Port Scan PCAP ---")
    with open('test_traffic/port_scan/port_scan.pcap', 'rb') as f:
        res = requests.post("http://localhost:8000/api/analyze/pcap", files={'file': f})
        data = res.json()
        print("Port Scan Alerts:", data['threats_found'])
        if data['threats_found'] > 0:
            print("PASS: Port Scan detected.")
        else:
            print("FAIL: Port Scan not detected!")
            sys.exit(1)

except Exception as e:
    print("Test Error:", e)
