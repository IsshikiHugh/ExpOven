"""Tests for the new config system (groups, meta config)."""

import os
import unittest
import tempfile
import shutil

from oven.oven import _load_group_config, _load_default_group_name


class TestLoadGroupConfig(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.groups_dir = os.path.join(self.tmpdir, 'ogroups')
        os.makedirs(self.groups_dir)
        # Point OVEN_HOME to the temp directory.
        self._old_env = os.environ.get('OVEN_HOME')
        os.environ['OVEN_HOME'] = self.tmpdir

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        if self._old_env is None:
            os.environ.pop('OVEN_HOME', None)
        else:
            os.environ['OVEN_HOME'] = self._old_env

    def test_load_valid_group(self):
        """Loading a group with one backend should return a list of dicts."""
        group_path = os.path.join(self.groups_dir, 'test.yaml')
        with open(group_path, 'w') as f:
            f.write(
                'backends:\n'
                '  - type: dingtalk\n'
                '    hook: https://example.com\n'
                '    secure_key: abc\n'
            )
        result = _load_group_config('test')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'dingtalk')

    def test_load_multi_backend_group(self):
        """Loading a group with multiple backends should return all."""
        group_path = os.path.join(self.groups_dir, 'multi.yaml')
        with open(group_path, 'w') as f:
            f.write(
                'backends:\n'
                '  - type: dingtalk\n'
                '    hook: https://example.com\n'
                '    secure_key: abc\n'
                '  - type: slack\n'
                '    hook: https://hooks.slack.com/test\n'
            )
        result = _load_group_config('multi')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['type'], 'dingtalk')
        self.assertEqual(result[1]['type'], 'slack')

    def test_load_missing_group_raises(self):
        """Loading a non-existent group should raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            _load_group_config('nonexistent')

    def test_load_empty_group_raises(self):
        """Loading a group with no backends should raise ValueError."""
        group_path = os.path.join(self.groups_dir, 'empty.yaml')
        with open(group_path, 'w') as f:
            f.write('backends:\n')
        with self.assertRaises(ValueError):
            _load_group_config('empty')


class TestLoadDefaultGroupName(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._old_env = os.environ.get('OVEN_HOME')
        os.environ['OVEN_HOME'] = self.tmpdir

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        if self._old_env is None:
            os.environ.pop('OVEN_HOME', None)
        else:
            os.environ['OVEN_HOME'] = self._old_env

    def test_reads_default_name(self):
        """Should return the default group name from config.yaml."""
        meta_path = os.path.join(self.tmpdir, 'config.yaml')
        with open(meta_path, 'w') as f:
            f.write('default: work\n')
        self.assertEqual(_load_default_group_name(), 'work')

    def test_missing_meta_raises(self):
        """Should raise FileNotFoundError when config.yaml is missing."""
        with self.assertRaises(FileNotFoundError):
            _load_default_group_name()

    def test_fallback_to_default(self):
        """If 'default' key is missing, should fall back to 'default'."""
        meta_path = os.path.join(self.tmpdir, 'config.yaml')
        with open(meta_path, 'w') as f:
            f.write('something_else: foo\n')
        self.assertEqual(_load_default_group_name(), 'default')


if __name__ == '__main__':
    unittest.main()
