"""Shared MockBackend for unit tests."""

from typing import Dict, List, Tuple
from oven.backends.api import NotifierBackendBase, RespStatus


class MockBackend(NotifierBackendBase):
    """A backend that records all notify() calls instead of making network requests."""

    def __init__(self, cfg: Dict = None):
        self.calls: List[Tuple[int, object]] = []
        self._meta = cfg or {}

    def notify(self, info) -> RespStatus:
        formatted = info.format_information()
        self.calls.append((info.current_signal, formatted))
        return RespStatus(has_err=False)

    def get_meta(self) -> Dict:
        return dict(self._meta)


def make_dingtalk_meta(cmd='test_cmd'):
    return {
        'host': None,
        'sec_key': 'test_sec_key',
        'backend': 'DingTalkBackend',
        'cmd': cmd,
    }


def make_feishu_meta(cmd='test_cmd'):
    return {
        'host': None,
        'signature': 'test_signature',
        'backend': 'FeishuBackend',
        'cmd': cmd,
    }


def make_slack_meta(cmd='test_cmd'):
    return {
        'host': None,
        'backend': 'SlackBackend',
        'cmd': cmd,
    }


def make_email_meta(cmd='test_cmd'):
    return {
        'smtp_server': 'smtp.test.com',
        'smtp_port': 587,
        'sender_email': 'sender@test.com',
        'sender_pwd': 'password',
        'receiver_email': 'receiver@test.com',
        'cmd': cmd,
    }
