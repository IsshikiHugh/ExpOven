"""Tests for the backend registry."""

import unittest

from oven.backends.registry import get_backend_classes, supported_types
from oven.backends.api import NotifierBackendBase
from oven.backends.api.info import ExpInfoBase, LogInfoBase


class TestRegistry(unittest.TestCase):
    def test_supported_types(self):
        """All four backends should be registered."""
        types = supported_types()
        self.assertEqual(types, ['dingtalk', 'email', 'feishu', 'slack'])

    def test_get_dingtalk(self):
        """get_backend_classes('dingtalk') returns correct tuple."""
        BackendCls, ExpCls, LogCls = get_backend_classes('dingtalk')
        self.assertTrue(issubclass(BackendCls, NotifierBackendBase))
        self.assertTrue(issubclass(ExpCls, ExpInfoBase))
        self.assertTrue(issubclass(LogCls, LogInfoBase))
        self.assertEqual(BackendCls.__name__, 'DingTalkBackend')

    def test_get_feishu(self):
        BackendCls, ExpCls, LogCls = get_backend_classes('feishu')
        self.assertEqual(BackendCls.__name__, 'FeishuBackend')

    def test_get_slack(self):
        BackendCls, ExpCls, LogCls = get_backend_classes('slack')
        self.assertEqual(BackendCls.__name__, 'SlackBackend')

    def test_get_email(self):
        BackendCls, ExpCls, LogCls = get_backend_classes('email')
        self.assertEqual(BackendCls.__name__, 'EmailBackend')

    def test_unknown_type_raises(self):
        """Unknown backend type should raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            get_backend_classes('telegram')
        self.assertIn('telegram', str(ctx.exception))
        self.assertIn('Supported types', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
