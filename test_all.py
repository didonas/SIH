import requests
import sys

print("Testing Health API...")
try:
    h = requests.get('http://localhost:8000/api/health', timeout=3)
    print("Health:", h.json())
except Exception as e:
    print("Health Failed:", e)

print("\nTesting Dashboard API...")
try:
    d = requests.get('http://localhost:8000/api/dashboard/summary', timeout=3)
    print("Dashboard:", list(d.json().keys()))
except Exception as e:
    print("Dashboard Failed:", e)

print("\nTesting SYN Flood PCAP Upload...")
try:
    with open('test_traffic/syn_flood/syn_flood.pcap', 'rb') as f:
        r = requests.post('http://localhost:8000/api/analyze/pcap', files={'file': f})
    print("SYN Flood Status:", r.status_code)
    print("SYN Flood Result:", r.json())
except Exception as e:
    print("Upload Failed:", e)
