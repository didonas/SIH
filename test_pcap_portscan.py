import requests
import sys

print("Testing Port Scan PCAP Upload...")
try:
    with open('test_traffic/port_scan/port_scan.pcap', 'rb') as f:
        r = requests.post('http://localhost:8000/api/analyze/pcap', files={'file': f})
    print("Port Scan Status:", r.status_code)
    print("Port Scan Threats Detected:", r.json().get('threats_detected'))
except Exception as e:
    print("Upload Failed:", e)
