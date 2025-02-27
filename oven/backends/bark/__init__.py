import json
import requests
from typing import Union, Dict, Tuple
import base64
import hashlib
import hmac
from datetime import datetime
from oven.backends.api import NotifierBackendBase, RespStatus

from .info import BarkExpInfo, BarkLogInfo


class BarkBackend(NotifierBackendBase):
    def __init__(self, cfg: Dict):
        # Validate the configuration.
        assert (
            'device_token' in cfg and '<?>' not in cfg['device_token']
        ), 'Please ensure the validity of "bark.device_token" field in the configuration file!'
        assert (
            'group' in cfg and '<?>' not in cfg['group']
        ), 'Please ensure the validity of "bark.group" field in the configuration file!'
        assert (
            'url' in cfg
        ), 'Please ensure the validity of "bark.url" field in the configuration file!'

        # Setup.
        self.cfg = cfg
        self.device_token = cfg['device_token']
        self.target_address = 'https://api.day.app/' + self.device_token
        self.icon = ''   # TODO: add icon support.

    def notify(self, info: BarkExpInfo):
        """
        bark the message.
        Check docs: https://bark.day.app/#/?id=bark
        """
        # 1. Prepare data dict.
        formatted_data = info.format_information()

        payload = {
            'title': formatted_data['title'],
            'body': formatted_data['content'],
            'group': self.cfg['group'],
            'icon': self.icon,
            'url': self.cfg['url'],
            'level': formatted_data['level'],
        }
        if '<?>' in self.cfg['url']:
            payload.pop('url')
        # 2. Post request and get response.
        has_err, err_msg = False, ''
        try:
            resp = requests.post(self.target_address, json=payload)
            resp_dict = json.loads(resp.text)
            has_err, err_msg = self._parse_resp(resp_dict)
        except Exception as e:
            has_err = True
            err_msg = f'Cannot send notification to bark: {e}'

        # 3. Return response dict.
        resp_status = RespStatus(has_err=has_err, err_msg=err_msg)
        return resp_status

    def get_meta(self) -> Dict:
        """Generate meta information for information object."""
        return {
            'host': self.cfg.get('host', None),
            'device_token': self.cfg.get('device_token', None),
            'backend': 'BarkBackend',
        }

    def _parse_resp(self, resp_dict) -> Tuple[bool, str]:
        """
        Reference: https://open.feishu.cn/community/articles/7298688341381546012
        Addition: according to test, if the message is sent successfully, the response will have `code=0`.
        """
        has_err, err_msg = False, ''
        if 'code' in resp_dict and resp_dict['code'] != 200:
            code = resp_dict['code']
            msg = resp_dict['msg']
            has_err, err_msg = True, f'[{code}] {msg}'
        return has_err, err_msg
