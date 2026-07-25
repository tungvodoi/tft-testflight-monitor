import os
import requests
from bs4 import BeautifulSoup

TESTFLIGHT_URL = "https://testflight.apple.com/join/q79npPHz"
# Fetches the webhook securely from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

def check_testflight():
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
    }
    
    try:
        response = requests.get(TESTFLIGHT_URL, headers=headers)
        if response.status_code != 200:
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        
        if "This beta is full" in page_text and "not accepting any new testers" not in page_text:
            send_discord_alert()
            
    except Exception as e:
        print(f"Error: {e}")

def send_discord_alert():
    data = {
        "content": f"🚨 **TFT PBE TESTFLIGHT SLOTS ARE OPEN!** 🚨\nGrab your spot: {TESTFLIGHT_URL}"
    }
    requests.post(DISCORD_WEBHOOK_URL, json=data)

if __name__ == "__main__":
    check_testflight()
