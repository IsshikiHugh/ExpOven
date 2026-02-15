"""Tests for Oven orchestration (ding_log, ding_func, ding_cmd)."""

import unittest
from unittest.mock import patch, MagicMock
import subprocess

from oven.backends.api import Signal
from oven.backends.dingtalk.info import DingTalkExpInfo, DingTalkLogInfo
from tests.mock_backend import MockBackend, make_dingtalk_meta


def _make_oven_with_mock():
    """Create an Oven instance bypassing _init_notifier, using MockBackend."""
    from oven.oven import Oven

    # Bypass __init__ which calls _init_notifier and needs a real config.
    oven = object.__new__(Oven)
    oven.backend = MockBackend(make_dingtalk_meta())
    oven.ExpInfoClass = DingTalkExpInfo
    oven.LogInfoClass = DingTalkLogInfo
    oven.cfg = {}
    return oven


class TestDingLog(unittest.TestCase):
    def test_ding_log_produces_one_notification(self):
        """ding_log() should produce exactly 1 notification (Signal.T via LogInfo)."""
        oven = _make_oven_with_mock()
        oven.ding_log('test message')
        self.assertEqual(len(oven.backend.calls), 1)
        self.assertEqual(oven.backend.calls[0][0], Signal.T)


class TestDingFunc(unittest.TestCase):
    def test_success_produces_two_notifications(self):
        """ding_func() on success: Signal.S then Signal.T."""
        oven = _make_oven_with_mock()

        @oven.ding_func
        def my_func():
            return 42

        result = my_func()
        self.assertEqual(result, 42)
        signals = [c[0] for c in oven.backend.calls]
        self.assertEqual(signals, [Signal.S, Signal.T])

    def test_exception_produces_two_notifications(self):
        """ding_func() on exception: Signal.S then Signal.E, returns None."""
        oven = _make_oven_with_mock()

        @oven.ding_func
        def failing_func():
            raise ValueError('boom')

        result = failing_func()
        self.assertIsNone(result)
        signals = [c[0] for c in oven.backend.calls]
        self.assertEqual(signals, [Signal.S, Signal.E])

    def test_func_with_args(self):
        """ding_func() should pass args and kwargs through correctly."""
        oven = _make_oven_with_mock()

        @oven.ding_func
        def add(a, b, extra=0):
            return a + b + extra

        result = add(1, 2, extra=10)
        self.assertEqual(result, 13)


class TestDingCmd(unittest.TestCase):
    @patch('oven.oven.subprocess.run')
    def test_success_produces_two_notifications(self, mock_run):
        """ding_cmd() on success: Signal.S then Signal.T."""
        mock_run.return_value = MagicMock(returncode=0)
        oven = _make_oven_with_mock()
        oven.ding_cmd('echo hello')
        signals = [c[0] for c in oven.backend.calls]
        self.assertEqual(signals, [Signal.S, Signal.T])
        mock_run.assert_called_once_with(
            'echo hello', shell=True, check=True, encoding='utf-8'
        )

    @patch('oven.oven.subprocess.run')
    def test_failure_produces_error_signal(self, mock_run):
        """ding_cmd() on CalledProcessError: Signal.S then Signal.E."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'bad_cmd')
        oven = _make_oven_with_mock()
        oven.ding_cmd('bad_cmd')
        signals = [c[0] for c in oven.backend.calls]
        self.assertEqual(signals, [Signal.S, Signal.E])


if __name__ == '__main__':
    unittest.main()
