#import os
import requests
from dotenv import load_dotenv

load_dotenv()


class SlackNotifier:
    def __init__(self, bot_token=None, channel_id=None):
        self.bot_token = bot_token or os.getenv('SLACK_BOT_TOKEN')
        self.channel_id = channel_id or os.getenv('SLACK_CHANNEL_ID')
        self.base_url = 'https://slack.com/api'

        self.headers = {
            'Authorization': f'Bearer {self.bot_token}',
            'Content-Type': 'application/json',
        }

    def send_message(self, message: str) -> dict:
        data = {'channel': self.channel_id, 'text': message}
        response = requests.post(
            f'{self.base_url}/chat.postMessage',
            json=data,
            headers=self.headers
        )
        return response.json()

    def update_message(self, ts: str, new_text: str) -> dict:
        data = {
            'channel': self.channel_id,
            'ts': ts,
            'text': new_text,
        }
        response = requests.post(
            f'{self.base_url}/chat.update',
            json=data,
            headers=self.headers
        )
        return response.json()
