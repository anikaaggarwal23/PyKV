import time
import requests

BASE_URL = "http://127.0.0.1:8000"

start = time.time()
for i in range(1000):
    requests.post(f"{BASE_URL}/set",
        json={"key": f"k{i}", "value": str(i)})
print("Benchmark Time:", time.time() - start)
