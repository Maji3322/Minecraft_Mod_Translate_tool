"""Regression tests for application configuration."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import __version__
from src.utils.config import Config


class ConfigVersionTests(unittest.TestCase):
    """Tests for version-related configuration behavior."""

    def test_get_app_version_uses_package_metadata(self):
        """The app version should come from package metadata, not pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()
        self.assertEqual(cfg.get_app_version(), __version__)


class ConfigFilePathTests(unittest.TestCase):
    """Tests for _config_file_path static method."""

    def test_frozen_uses_executable_dir(self):
        """In frozen (compiled) mode, config file is next to the executable."""
        fake_exe = str(Path('C:/app/dist/app.exe'))
        with patch.object(sys, 'frozen', True, create=True), \
             patch.object(sys, 'executable', fake_exe):
            path = Config._config_file_path()
        expected = Path('C:/app/dist') / 'ollama_config.json'
        self.assertEqual(path, expected)

    def test_dev_mode_uses_project_root(self):
        """In dev mode, config file is at the project root (3 levels above config.py)."""
        with patch('sys.frozen', False, create=True):
            path = Config._config_file_path()
        # tests/test_config.py → parent = tests/ → parent = project root
        expected = Path(__file__).parent.parent / 'ollama_config.json'
        self.assertEqual(path, expected)


class ConfigSaveTests(unittest.TestCase):
    """Tests for Config.save()."""

    def test_save_writes_url_and_model(self):
        """save() writes current URL and model to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            # Patch before Config() so __init__'s load() also uses the temp path
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()
                cfg.OLLAMA_BASE_URL = 'http://example.com:11434'
                cfg.OLLAMA_MODEL = 'my-model'
                cfg.save()

            data = json.loads(config_path.read_text(encoding='utf-8'))

        self.assertEqual(data['ollama_base_url'], 'http://example.com:11434')
        self.assertEqual(data['ollama_model'], 'my-model')

    def test_save_does_not_raise_on_write_error(self):
        """save() logs a warning but does not raise if write fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()
            # Now point to an unwritable location
            with patch.object(Config, '_config_file_path', lambda self=None: Path('/nonexistent/dir/config.json')):
                cfg.save()  # Should not raise


class ConfigLoadTests(unittest.TestCase):
    """Tests for Config.load()."""

    def test_load_reads_url_and_model(self):
        """load() sets URL and model from valid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            config_path.write_text(json.dumps({
                'ollama_base_url': 'http://remote:11434',
                'ollama_model': 'custom-model',
            }), encoding='utf-8')

            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()

        self.assertEqual(cfg.OLLAMA_BASE_URL, 'http://remote:11434')
        self.assertEqual(cfg.OLLAMA_MODEL, 'custom-model')
        self.assertFalse(cfg.config_corrupted)

    def test_load_creates_file_when_missing(self):
        """load() auto-creates ollama_config.json with defaults when file is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            # Patch before Config() so both __init__'s load() and save() use temp path
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()

            self.assertTrue(config_path.exists())
            data = json.loads(config_path.read_text(encoding='utf-8'))

        self.assertEqual(data['ollama_base_url'], Config.OLLAMA_DEFAULT_BASE_URL)
        self.assertEqual(data['ollama_model'], Config.OLLAMA_DEFAULT_MODEL)
        self.assertFalse(cfg.config_corrupted)

    def test_load_sets_corrupted_flag_on_bad_json(self):
        """load() sets config_corrupted=True and keeps defaults when JSON is invalid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            config_path.write_text('{ not valid json', encoding='utf-8')

            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()

        self.assertTrue(cfg.config_corrupted)
        self.assertEqual(cfg.OLLAMA_BASE_URL, Config.OLLAMA_DEFAULT_BASE_URL)
        self.assertEqual(cfg.OLLAMA_MODEL, Config.OLLAMA_DEFAULT_MODEL)

    def test_config_corrupted_is_false_by_default(self):
        """config_corrupted is False on a fresh Config with a missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'ollama_config.json'
            with patch.object(Config, '_config_file_path', lambda self=None: config_path):
                cfg = Config()
        self.assertFalse(cfg.config_corrupted)
