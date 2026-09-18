import requests
import time

BASE_URL = 'http://localhost:8000'

def test_endpoint(url):
    print(f"Testing {url} ... ", end="")
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            print("OK")
            return True
        else:
            print(f"FAIL ({r.status_code})")
            return False
    except Exception as e:
        print(f"FAIL ({e})")
        return False

time.sleep(2) # let server start

endpoints = [
    '/api/health',
    '/api/dashboard/summary',
    '/api/dashboard/analytics',
    '/api/alerts',
    '/api/system',
    '/api/live/interfaces',
    '/api/live/status'
]

success = True
for ep in endpoints:
    success &= test_endpoint(BASE_URL + ep)

print("\nTesting PCAP Uploads:")
def test_pcap(path):
    print(f"Testing {path} ... ", end="")
    try:
        with open(path, 'rb') as f:
            r = requests.post(BASE_URL + '/api/analyze/pcap', files={'file': f}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            print(f"OK (Threats: {data.get('threats_detected')})")
        else:
            print(f"FAIL ({r.status_code}: {r.text})")
    except Exception as e:
        print(f"FAIL ({e})")

test_pcap('test_traffic/syn_flood/syn_flood.pcap')
test_pcap('test_traffic/port_scan/port_scan.pcap')

# Invalid PCAP
print("Testing invalid file ... ", end="")
try:
    r = requests.post(BASE_URL + '/api/analyze/pcap', files={'file': ('invalid.txt', b'this is not a pcap')})
    if r.status_code == 400:
        print("OK (400 as expected)")
    else:
        print(f"FAIL (expected 400, got {r.status_code})")
except Exception as e:
    print(f"FAIL ({e})")

print("All tests completed.")
