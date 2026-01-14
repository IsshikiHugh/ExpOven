import json
import requests
from typing import Union, Dict, Tuple

from oven.consts import REQ_TIMEOUT
from oven.backends.api import NotifierBackendBase, RespStatus

from .info import SlackExpInfo, SlackLogInfo


class SlackBackend(NotifierBackendBase):
    def __init__(self, cfg: Dict):
        # Validate the configuration.
        assert (
            'hook' in cfg and '<?>' not in cfg['hook']
        ), 'Please ensure the validity of "slack.hook" field in the configuration file!'

        # Setup.
        self.cfg = cfg
        self.url = cfg['hook']

    def notify(self, info: SlackExpInfo):
        """
        Ask the bot to send raw string message.
        Check docs: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks
        """

        # 1. Prepare data dict.
        data = info.format_information()

        # 2. Post request and get response.
        has_err, err_msg = False, ''
        try:
            resp = requests.post(self.url, json=data, timeout=REQ_TIMEOUT)
            has_err, err_msg = self._parse_resp(resp.text)
        except Exception as e:
            has_err = True
            err_msg = f'Cannot send message to Slack: {e}'

        # 3. Return response dict.
        resp_status = RespStatus(has_err=has_err, err_msg=err_msg)
        return resp_status

    def get_meta(self) -> Dict:
        """Generate meta information for information object."""
        return {
            'host': self.cfg.get('host', None),
            'backend': 'SlackBackend',
        }

    # ================ #
    # Utils functions. #
    # ================ #

    def _parse_resp(self, resp_content) -> Tuple[bool, str]:
        has_err, err_msg = False, ''
        if resp_content != 'ok':
            has_err, err_msg = True, resp_content
        return has_err, err_msg
