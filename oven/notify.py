import os
import json
import requests
from typing import Dict, Tuple

from dotenv import load_dotenv
from oven.consts import REQ_TIMEOUT
from oven.backends.api import NotifierBackendBase, RespStatus

from .info import SlackLogInfo  # You can rename or adapt as needed

load_dotenv()


class SlackBackend(NotifierBackendBase):
    def __init__(self, cfg: Dict):
        assert (
            'bot_token' in cfg and '<?>' not in cfg['bot_token']
        ), 'Please ensure the validity of "slack.bot_token" in the config!'

        assert (
            'channel_id' in cfg and '<?>' not in cfg['channel_id']
        ), 'Please ensure the validity of "slack.channel_id" in the config!'

        self.cfg = cfg
        self.bot_token = cfg['bot_token']
        self.channel_id = cfg['channel_id']
        self.base_url = 'https://slack.com/api'

        self.headers = {
            'Authorization': f'Bearer {self.bot_token}',
            'Content-Type': 'application/json',
        }

    def notify(self, info: SlackLogInfo):
        """Send a raw string message to Slack"""
        data = {
            'channel': self.channel_id,
            'text': info.format_information(),
        }

        has_err, err_msg = False, ''
        try:
            resp = requests.post(f'{self.base_url}/chat.postMessage', json=data, headers=self.headers, timeout=REQ_TIMEOUT)
            resp_dict = json.loads(resp.text)
            has_err, err_msg = self._parse_resp(resp_dict)
        except Exception as e:
            has_err = True
            err_msg = f'Cannot send message to Slack: {e}'

        return RespStatus(has_err=has_err, err_msg=err_msg)

    def get_meta(self) -> Dict:
        return {
            'channel': self.cfg['channel_id'],
            'backend': 'SlackBackend',
        }

    def _parse_resp(self, resp_dict) -> Tuple[bool, str]:
        has_err, err_msg = False, ''
        if not resp_dict.get('ok', False):
            has_err = True
            err_msg = f"[{resp_dict.get('error', 'unknown_error')}] Failed to send message"
        return has_err, err_msg
