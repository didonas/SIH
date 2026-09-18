import requests

with open("mixed_traffic.pcap", "rb") as f:
    res = requests.post("http://localhost:8000/api/analyze/pcap", files={"file": f})
    data = res.json()
    print("Status:", res.status_code)
    print("Alerts array length:", len(data.get("alerts", [])))
    if data.get("alerts"):
        alert = data["alerts"][0]
        print("First alert keys:", list(alert.keys()))
        print("First alert severity:", alert.get("severity"))
        print("First alert evidence:", alert.get("evidence"))
