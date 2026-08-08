import os
import time
import requests
from bs4 import BeautifulSoup

TESTFLIGHT_URL = "https://testflight.apple.com/join/q79npPHz"

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
PUSHCUT_WEBHOOK_URL = os.environ.get("PUSHCUT_WEBHOOK")

POLL_INTERVAL_SECONDS = 20                 # how often to check
ALERT_COOLDOWN_SECONDS = 5 * 60            # don't re-alert more than once per 5 min while still open
MAX_RUNTIME_SECONDS = 5 * 3600 + 45 * 60   # 5h45m, safely under the 6h Actions job limit

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) '
                  'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
}


def is_slot_open(session):
    """Returns True if open, False if full, None if the check itself failed."""
    try:
        response = session.get(TESTFLIGHT_URL, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Non-200 response: {response.status_code}")
            return None

        page_text = BeautifulSoup(response.text, 'html.parser').get_text()
        full = "This beta is full" in page_text or "not accepting any new testers" in page_text
        return not full
    except Exception as e:
        print(f"Check failed: {e}")
        return None


def send_discord_alert():
    if not DISCORD_WEBHOOK_URL:
        print("No DISCORD_WEBHOOK set, skipping Discord alert")
        return
    data = {
        "content": f"🚨 **TFT PBE TESTFLIGHT SLOTS ARE OPEN!** 🚨\nGrab your spot: {TESTFLIGHT_URL}"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")


def send_pushcut_alert():
    if not PUSHCUT_WEBHOOK_URL:
        print("No PUSHCUT_WEBHOOK set, skipping Pushcut alert")
        return
    try:
        requests.post(PUSHCUT_WEBHOOK_URL, json={}, timeout=10)
    except Exception as e:
        print(f"Failed to trigger Pushcut: {e}")


def main():
    start_time = time.time()
    last_alert_time = 0
    session = requests.Session()

    print("Starting poll loop...")
    while time.time() - start_time < MAX_RUNTIME_SECONDS:
        open_now = is_slot_open(session)

        if open_now:
            now = time.time()
            if now - last_alert_time > ALERT_COOLDOWN_SECONDS:
                print("Slot open — sending alerts")
                send_discord_alert()
                send_pushcut_alert()
                last_alert_time = now
            else:
                print("Slot still open (cooldown active, not re-alerting)")
        elif open_now is False:
            print("Beta full, nothing to do")
        # open_now is None → check failed, just loop again

        time.sleep(POLL_INTERVAL_SECONDS)

    print("Runtime budget reached, exiting so the next scheduled run can take over")


if __name__ == "__main__":
    main()
