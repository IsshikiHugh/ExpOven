"""Tests for signal lifecycle in ExpInfoBase and LogInfoBase."""

import unittest

from oven.backends.api import Signal
from oven.backends.dingtalk.info import DingTalkExpInfo, DingTalkLogInfo
from tests.mock_backend import MockBackend, make_dingtalk_meta


class TestExpInfoSignalLifecycle(unittest.TestCase):
    """ExpInfoBase.__init__ triggers I then S; update_signal triggers further signals."""

    def setUp(self):
        self.backend = MockBackend()

    def test_init_triggers_start_notification(self):
        """ExpInfoBase.__init__ should trigger exactly one notification (Signal.S)."""
        meta = make_dingtalk_meta()
        DingTalkExpInfo(self.backend, exp_meta_info=meta, description='')
        self.assertEqual(len(self.backend.calls), 1)
        self.assertEqual(self.backend.calls[0][0], Signal.S)

    def test_terminate_signal(self):
        """update_signal(Signal.T) should trigger a terminate notification."""
        meta = make_dingtalk_meta()
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description=''
        )
        self.backend.calls.clear()

        info.update_signal(Signal.T)
        self.assertEqual(len(self.backend.calls), 1)
        self.assertEqual(self.backend.calls[0][0], Signal.T)

    def test_exception_signal_with_description(self):
        """update_signal(Signal.E, description) should trigger exception notification."""
        meta = make_dingtalk_meta()
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description=''
        )
        self.backend.calls.clear()

        info.update_signal(Signal.E, description='something went wrong')
        self.assertEqual(len(self.backend.calls), 1)
        self.assertEqual(self.backend.calls[0][0], Signal.E)

    def test_progress_signal(self):
        """update_signal(Signal.P) should trigger progress notification."""
        meta = make_dingtalk_meta()
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description=''
        )
        self.backend.calls.clear()

        info.update_signal(Signal.P, description='50% done')
        self.assertEqual(len(self.backend.calls), 1)
        self.assertEqual(self.backend.calls[0][0], Signal.P)

    def test_full_lifecycle_sequence(self):
        """Full lifecycle: S -> P -> T should produce 3 notifications in order."""
        meta = make_dingtalk_meta()
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description=''
        )
        info.update_signal(Signal.P, description='progress')
        info.update_signal(Signal.T)

        signals = [call[0] for call in self.backend.calls]
        self.assertEqual(signals, [Signal.S, Signal.P, Signal.T])

    def test_error_lifecycle_sequence(self):
        """Error lifecycle: S -> E should produce 2 notifications in order."""
        meta = make_dingtalk_meta()
        info = DingTalkExpInfo(
            self.backend, exp_meta_info=meta, description=''
        )
        info.update_signal(Signal.E, description='crash')

        signals = [call[0] for call in self.backend.calls]
        self.assertEqual(signals, [Signal.S, Signal.E])


class TestLogInfoSignalLifecycle(unittest.TestCase):
    """LogInfoBase.__init__ triggers I then T (single message lifecycle)."""

    def setUp(self):
        self.backend = MockBackend()

    def test_log_triggers_single_terminate(self):
        """LogInfoBase.__init__ should trigger exactly one notification (Signal.T)."""
        meta = make_dingtalk_meta()
        DingTalkLogInfo(self.backend, exp_meta_info=meta, description='hello')
        self.assertEqual(len(self.backend.calls), 1)
        self.assertEqual(self.backend.calls[0][0], Signal.T)


class TestSignalValidity(unittest.TestCase):
    """Test Signal.is_valid and Signal.is_noisy helpers."""

    def test_valid_signals(self):
        for sig in [
            Signal.U,
            Signal.I,
            Signal.S,
            Signal.P,
            Signal.T,
            Signal.E,
        ]:
            self.assertTrue(Signal.is_valid(sig))

    def test_invalid_signal(self):
        self.assertFalse(Signal.is_valid(99))

    def test_noisy_signals(self):
        for sig in [Signal.S, Signal.P, Signal.T, Signal.E]:
            self.assertTrue(Signal.is_noisy(sig))

    def test_non_noisy_signals(self):
        for sig in [Signal.U, Signal.I]:
            self.assertFalse(Signal.is_noisy(sig))


if __name__ == '__main__':
    unittest.main()
