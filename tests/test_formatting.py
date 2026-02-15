"""Tests for backend-specific formatting (format_information)."""

import unittest

from oven.backends.api import Signal
from oven.backends.dingtalk.info import DingTalkExpInfo, DingTalkLogInfo
from oven.backends.feishu.info import FeishuExpInfo, FeishuLogInfo
from oven.backends.slack.info import SlackExpInfo, SlackLogInfo
from oven.backends.email.info import EmailExpInfo, EmailLogInfo
from tests.mock_backend import (
    MockBackend,
    make_dingtalk_meta,
    make_feishu_meta,
    make_slack_meta,
    make_email_meta,
)


class TestDingTalkFormatting(unittest.TestCase):
    def setUp(self):
        self.backend = MockBackend()

    def test_exp_info_format_returns_string(self):
        meta = make_dingtalk_meta(cmd='train.py')
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description='run 1'
        )
        result = info.format_information()
        self.assertIsInstance(result, str)
        self.assertIn('train.py', result)

    def test_exp_info_format_after_terminate(self):
        meta = make_dingtalk_meta(cmd='train.py')
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description=''
        )
        info.update_signal(Signal.T)
        result = info.format_information()
        self.assertIsInstance(result, str)
        self.assertIn('Done', result)

    def test_log_info_format_returns_string(self):
        meta = make_dingtalk_meta()
        info = DingTalkLogInfo(
            self.backend, exp_meta_info=meta, description='log msg'
        )
        result = info.format_information()
        self.assertIsInstance(result, str)
        self.assertIn('log msg', result)

    def test_exp_info_has_host(self):
        meta = make_dingtalk_meta()
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description=''
        )
        result = info.format_information()
        self.assertIn('@', result)

    def test_exp_info_has_title(self):
        meta = make_dingtalk_meta()
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description=''
        )
        title = info.get_title()
        self.assertIn('test_sec_key', title)


class TestFeishuFormatting(unittest.TestCase):
    def setUp(self):
        self.backend = MockBackend()

    def test_exp_info_format_returns_dict(self):
        meta = make_feishu_meta(cmd='train.py')
        info = FeishuExpInfo(
            self.backend, exp_meta_info=meta, description='run 1'
        )
        result = info.format_information()
        self.assertIsInstance(result, dict)
        self.assertIn('schema', result)
        self.assertIn('header', result)
        self.assertIn('body', result)
        self.assertIn('elements', result['body'])

    def test_exp_info_format_after_terminate(self):
        meta = make_feishu_meta(cmd='train.py')
        info = FeishuExpInfo(self.backend, exp_meta_info=meta, description='')
        info.update_signal(Signal.T)
        result = info.format_information()
        self.assertIsInstance(result, dict)

    def test_log_info_format_returns_dict(self):
        meta = make_feishu_meta()
        info = FeishuLogInfo(
            self.backend, exp_meta_info=meta, description='log msg'
        )
        result = info.format_information()
        self.assertIsInstance(result, dict)
        self.assertIn('body', result)
        elements = result['body']['elements']
        self.assertTrue(len(elements) > 0)
        self.assertEqual(elements[0]['tag'], 'markdown')

    def test_exp_info_header_has_host(self):
        meta = make_feishu_meta()
        info = FeishuExpInfo(self.backend, exp_meta_info=meta, description='')
        result = info.format_information()
        title = result['header']['title']['content']
        self.assertIn('@', title)


class TestSlackFormatting(unittest.TestCase):
    def setUp(self):
        self.backend = MockBackend()

    def test_exp_info_format_returns_dict_with_blocks(self):
        meta = make_slack_meta(cmd='train.py')
        info = SlackExpInfo(
            self.backend, exp_meta_info=meta, description='run 1'
        )
        result = info.format_information()
        self.assertIsInstance(result, dict)
        self.assertIn('blocks', result)
        self.assertIsInstance(result['blocks'], list)
        self.assertTrue(len(result['blocks']) > 0)

    def test_exp_info_format_after_terminate(self):
        meta = make_slack_meta(cmd='train.py')
        info = SlackExpInfo(self.backend, exp_meta_info=meta, description='')
        info.update_signal(Signal.T)
        result = info.format_information()
        self.assertIn('blocks', result)

    def test_log_info_format_returns_dict_with_blocks(self):
        meta = make_slack_meta()
        info = SlackLogInfo(
            self.backend, exp_meta_info=meta, description='log msg'
        )
        result = info.format_information()
        self.assertIsInstance(result, dict)
        self.assertIn('blocks', result)

    def test_exp_info_context_block(self):
        meta = make_slack_meta()
        info = SlackExpInfo(self.backend, exp_meta_info=meta, description='')
        result = info.format_information()
        context_block = result['blocks'][0]
        self.assertEqual(context_block['type'], 'context')

    def test_exp_info_has_divider(self):
        meta = make_slack_meta()
        info = SlackExpInfo(self.backend, exp_meta_info=meta, description='')
        result = info.format_information()
        last_block = result['blocks'][-1]
        self.assertEqual(last_block['type'], 'divider')


class TestEmailFormatting(unittest.TestCase):
    def setUp(self):
        self.backend = MockBackend()

    def test_exp_info_format_returns_dict(self):
        meta = make_email_meta(cmd='train.py')
        info = EmailExpInfo(
            self.backend, exp_meta_info=meta, description='run 1'
        )
        result = info.format_information()
        self.assertIsInstance(result, dict)
        self.assertIn('subject', result)
        self.assertIn('content', result)

    def test_exp_info_format_after_terminate(self):
        meta = make_email_meta(cmd='train.py')
        info = EmailExpInfo(self.backend, exp_meta_info=meta, description='')
        info.update_signal(Signal.T)
        result = info.format_information()
        self.assertIn('subject', result)
        self.assertIn('content', result)

    def test_log_info_format_returns_dict(self):
        meta = make_email_meta()
        info = EmailLogInfo(
            self.backend, exp_meta_info=meta, description='log msg'
        )
        result = info.format_information()
        self.assertIsInstance(result, dict)
        self.assertIn('subject', result)
        self.assertIn('content', result)
        self.assertEqual(result['content'], 'log msg')

    def test_exp_info_subject_has_host(self):
        meta = make_email_meta()
        info = EmailExpInfo(self.backend, exp_meta_info=meta, description='')
        result = info.format_information()
        self.assertIn('@', result['subject'])


if __name__ == '__main__':
    unittest.main()
