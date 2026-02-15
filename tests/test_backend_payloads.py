"""Tests that real backends construct the correct HTTP/SMTP payloads."""

import unittest
from unittest.mock import patch, MagicMock
import json

from oven.backends.api import Signal
from oven.backends.dingtalk import DingTalkBackend
from oven.backends.dingtalk.info import DingTalkExpInfo
from oven.backends.feishu import FeishuBackend
from oven.backends.feishu.info import FeishuExpInfo
from oven.backends.slack import SlackBackend
from oven.backends.slack.info import SlackExpInfo
from oven.backends.email import EmailBackend
from oven.backends.email.info import EmailExpInfo


class TestDingTalkPayload(unittest.TestCase):
    @patch('oven.backends.dingtalk.requests.post')
    def test_sends_markdown_payload(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({'errcode': 0, 'errmsg': 'ok'})
        mock_post.return_value = mock_resp

        cfg = {
            'hook': 'https://oapi.dingtalk.com/robot/send?access_token=test',
            'secure_key': 'test_key',
            'backend': 'dingtalk',
        }
        backend = DingTalkBackend(cfg)
        meta = backend.get_meta()
        meta['cmd'] = 'python train.py'
        info = DingTalkExpInfo(backend, exp_meta_info=meta, description='')

        # The notify() call during __init__ already posted.
        self.assertTrue(mock_post.called)
        call_kwargs = mock_post.call_args
        data = (
            call_kwargs[1]['json']
            if 'json' in call_kwargs[1]
            else call_kwargs[0][0]
        )
        self.assertEqual(data['msgtype'], 'markdown')
        self.assertIn('markdown', data)
        self.assertIn('title', data['markdown'])
        self.assertIn('text', data['markdown'])


class TestFeishuPayload(unittest.TestCase):
    @patch('oven.backends.feishu.requests.post')
    def test_sends_interactive_payload(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.text = json.dumps({'code': 0, 'msg': 'ok'})
        mock_post.return_value = mock_resp

        cfg = {
            'hook': 'https://open.feishu.cn/open-apis/bot/v2/hook/test',
            'signature': 'test_sig',
            'backend': 'feishu',
        }
        backend = FeishuBackend(cfg)
        meta = backend.get_meta()
        meta['cmd'] = 'python train.py'
        info = FeishuExpInfo(backend, exp_meta_info=meta, description='')

        self.assertTrue(mock_post.called)
        call_kwargs = mock_post.call_args
        data = (
            call_kwargs[1]['json']
            if 'json' in call_kwargs[1]
            else call_kwargs[0][0]
        )
        self.assertEqual(data['msg_type'], 'interactive')
        self.assertIn('card', data)
        self.assertIn('timestamp', data)
        self.assertIn('sign', data)


class TestSlackPayload(unittest.TestCase):
    @patch('oven.backends.slack.requests.post')
    def test_sends_blocks_payload(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.text = 'ok'
        mock_post.return_value = mock_resp

        cfg = {
            'hook': 'https://hooks.slack.com/services/test',
            'backend': 'slack',
        }
        backend = SlackBackend(cfg)
        meta = backend.get_meta()
        meta['cmd'] = 'python train.py'
        info = SlackExpInfo(backend, exp_meta_info=meta, description='')

        self.assertTrue(mock_post.called)
        call_kwargs = mock_post.call_args
        data = (
            call_kwargs[1]['json']
            if 'json' in call_kwargs[1]
            else call_kwargs[0][0]
        )
        self.assertIn('blocks', data)
        self.assertIsInstance(data['blocks'], list)


class TestEmailPayload(unittest.TestCase):
    @patch('oven.backends.email.smtplib.SMTP')
    def test_sends_email_via_smtp(self, mock_smtp_class):
        mock_server = MagicMock()
        mock_smtp_class.return_value = mock_server

        cfg = {
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'sender_email': 'sender@test.com',
            'sender_pwd': 'password',
            'receiver_email': 'receiver@test.com',
            'backend': 'email',
        }
        backend = EmailBackend(cfg)
        meta = backend.get_meta()
        meta['cmd'] = 'python train.py'
        info = EmailExpInfo(backend, exp_meta_info=meta, description='')

        # Verify SMTP calls.
        mock_smtp_class.assert_called_with('smtp.test.com', 587)
        mock_server.starttls.assert_called()
        mock_server.login.assert_called_with('sender@test.com', 'password')
        mock_server.sendmail.assert_called()
        # Verify sendmail args.
        sendmail_args = mock_server.sendmail.call_args[0]
        self.assertEqual(sendmail_args[0], 'sender@test.com')
        self.assertEqual(sendmail_args[1], 'receiver@test.com')


if __name__ == '__main__':
    unittest.main()
