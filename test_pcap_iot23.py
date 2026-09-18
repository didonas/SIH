import requests
import sys
import time

print("Testing IoT-23 PCAP Upload...")
t0 = time.time()
try:
    with open('test_traffic/iot-23/2018-12-21-15-50-14-192.168.1.195.pcap', 'rb') as f:
        r = requests.post('http://localhost:8000/api/analyze/pcap', files={'file': f})
    print("IoT-23 Status:", r.status_code)
    try:
        data = r.json()
        print("IoT-23 Threats Detected:", data.get('threats_detected'))
        print("Flows analyzed:", data.get('flows_analyzed'))
    except:
        print("Response:", r.text)
    print(f"Time taken: {time.time()-t0:.2f}s")
except Exception as e:
    print("Upload Failed:", e)
