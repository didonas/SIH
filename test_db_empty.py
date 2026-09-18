import requests
import time

max_retries = 5
for _ in range(max_retries):
    try:
        res = requests.get("http://localhost:8000/api/dashboard/summary")
        print(res.json())
        break
    except Exception as e:
        time.sleep(2)
