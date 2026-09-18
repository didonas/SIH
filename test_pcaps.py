import requests

with open('test_traffic/syn_flood/syn_flood.pcap', 'rb') as f:
    res = requests.post("http://localhost:8000/api/analyze/pcap", files={'file': f})
    data = res.json()
    alerts = data.get('alerts', [])
    print("SYN Flood Alerts generated:", len(alerts))
    for a in alerts[:2]:
        print(" -", a['threat_type'])

with open('test_traffic/port_scan/port_scan.pcap', 'rb') as f:
    res = requests.post("http://localhost:8000/api/analyze/pcap", files={'file': f})
    data = res.json()
    alerts = data.get('alerts', [])
    print("Port Scan Alerts generated:", len(alerts))
    for a in alerts[:2]:
        print(" -", a['threat_type'])
