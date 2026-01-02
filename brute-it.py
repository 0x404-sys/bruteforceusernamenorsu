import requests
import threading
import queue
import time
import argparse

URL = "https://sms.norsureg-apps.com/check-username"

parser = argparse.ArgumentParser(description="Username checker")
parser.add_argument("-w", "--wordlist", required=True, help="Username wordlist")
parser.add_argument("-t", "--threads", type=int, default=5)
parser.add_argument("-d", "--delay", type=float, default=0.5)
parser.add_argument("--retries", type=int, default=2)
parser.add_argument("--proxy", help="Proxy (http://127.0.0.1:8080)")
parser.add_argument("--test", action="store_true")
args = parser.parse_args()

PROXIES = {"http": args.proxy, "https": args.proxy} if args.proxy else None

q = queue.Queue()
found_event = threading.Event()

checked = 0
total = 0
found_count = 0
failed_count = 0

lock = threading.Lock()


def fake_response(username):
    return {"exists": username.lower() == "admin"}


def worker():
    global checked, found_count, failed_count

    while not q.empty() and not found_event.is_set():
        username = q.get()
        success = False

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
                    with lock:
                        found_count += 1
                    print(f"\n[FOUND] Username exists: {username}")
                    with open("found.txt", "a") as f:
                        f.write(username + "\n")
                    found_event.set()

                success = True
                break

            except Exception:
                time.sleep(1)

        if not success:
            with lock:
                failed_count += 1

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

print("\n========== SUMMARY ==========")
print(f"Checked: {checked}")
print(f"Found usernames: {found_count}")
print(f"Failed: {failed_count}")
print("Done.")
