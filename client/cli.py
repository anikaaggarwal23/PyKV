import argparse
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def safe_request(method, url, **kwargs):
    for _ in range(3):
        try:
            return method(url, **kwargs)
        except Exception:
            time.sleep(0.5)
    raise Exception("Server not responding")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["get", "set", "delete"])
    parser.add_argument("--key")
    parser.add_argument("--value")
    args = parser.parse_args()

    if args.command == "set":
        safe_request(requests.post, f"{BASE_URL}/set",
            json={"key": args.key, "value": args.value})

    elif args.command == "get":
        print(safe_request(requests.get, f"{BASE_URL}/get/{args.key}").json())

    elif args.command == "delete":
        safe_request(requests.delete, f"{BASE_URL}/delete/{args.key}")

if __name__ == "__main__":
    main()
