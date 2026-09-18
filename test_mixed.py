import requests

with open("mixed_traffic.pcap", "rb") as f:
    res = requests.post("http://localhost:8000/api/analyze/pcap", files={"file": f})
    print(res.status_code)
    print(res.json())
