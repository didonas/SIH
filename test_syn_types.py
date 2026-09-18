import requests

with open('test_traffic/syn_flood/syn_flood.pcap', 'rb') as f:
    res = requests.post("http://localhost:8000/api/analyze/pcap", files={'file': f})
    data = res.json()
    alerts = data.get('alerts', [])
    types = set(a['threat_type'] for a in alerts)
    print("SYN Flood Alert Types:", types)
