# notify.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

def send_slack_message(message: str):
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "channel": SLACK_CHANNEL_ID,
        "text": message
    }

    response = requests.post("https://slack.com/api/chat.postMessage", json=data, headers=headers)
    return response.json()



#You can update an existing message by using the message ts value:


# Send the initial message
response = send_slack_message("🔄 Processing task...")

# Get timestamp to update later
ts = response.get("ts")

# Update the message after progress
update_data = {
    "channel": SLACK_CHANNEL_ID,
    "ts": ts,
    "text": " Task 50% complete"
}
requests.post("https://slack.com/api/chat.update", json=update_data, headers={
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    "Content-Type": "application/json"
})