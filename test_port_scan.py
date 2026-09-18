import requests
import time
import json

time.sleep(2) # wait for uvicorn to boot

with open("test_traffic/port_scan/port_scan.pcap", "rb") as f:
    res = requests.post("http://localhost:8000/api/analyze/pcap", files={"file": f})
    
data = res.json()
print("Status:", res.status_code)
print("Threats detected:", data.get('threats_detected'))
print("Flows analyzed:", data.get('flows_analyzed'))
if data.get('alerts'):
    alert = data['alerts'][0]
    print("Alert Threat Type:", alert['threat_type'])
    print("Alert Severity:", alert['severity'])
    print("Alert Source IP:", alert['source_ip'])
    print("Alert Destination IP:", alert['destination_ip'])
    print("Alert Risk Score:", alert['risk_score'])
    print("Alert Evidence:", alert['evidence'])
