"""Regression tests for application configuration."""

import unittest

from src import __version__
from src.utils.config import Config


class ConfigVersionTests(unittest.TestCase):
    """Tests for version-related configuration behavior."""

    def test_get_app_version_uses_package_metadata(self):
        """The app version should come from package metadata, not pyproject.toml."""
        config = Config()

        self.assertEqual(config.get_app_version(), __version__)
