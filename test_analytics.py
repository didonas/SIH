import requests
import time

try:
    with open("mixed_traffic.pcap", "rb") as f:
        res = requests.post("http://localhost:8000/api/analyze/pcap", files={"file": f})
        print("Analysis status:", res.status_code)
except Exception as e:
    print("Could not upload pcap", e)

time.sleep(2)
res = requests.get("http://localhost:8000/api/dashboard/analytics")
print("Analytics HTTP:", res.status_code)
data = res.json()
print("Metrics keys:", data["metrics"].keys())
print("Distributions protocols:", data["distributions"]["protocols"])
print("Top 1 Source:", data["distributions"]["top_sources"][0] if data["distributions"]["top_sources"] else None)
