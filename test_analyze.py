import requests

url = 'http://localhost:8000/api/analyze/pcap'
file_path = 'test_traffic/syn_flood/syn_flood.pcap'

with open(file_path, 'rb') as f:
    files = {'file': (file_path, f, 'application/vnd.tcpdump.pcap')}
    response = requests.post(url, files=files)
    
print(response.status_code)
print(response.json())
