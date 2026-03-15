"""Configuration management for the application."""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

from src import __version__

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the application."""

    # Minecraft version to pack format mapping
    VERSION_TO_PACK_FORMAT: Dict[str, int] = {
        "1.13 ~ 1.14.4": 4,
        "1.15 ~ 1.16.1": 5,
        "1.16.2 ~ 1.16.5": 6,
        "1.17 ~ 1.17.1": 7,
        "1.18 ~ 1.18.2": 8,
        "1.19 ~ 1.19.2": 9,
        "1.19.3": 12,
        "1.19.4": 13,
        "1.20 ~ 1.20.1": 15,
        "1.20.2": 18,
        "1.20.3 ~ 1.20.4": 22,
        "1.20.5 ~ 1.20.6": 32,
        "1.21 ~ 1.21.3": 35,
        "1.21.4~": 46,
    }

    @staticmethod
    def _config_file_path() -> Path:
        """Return the path to the JSON config file.

        In frozen (compiled) mode: next to the executable.
        In dev mode: at the project root (3 levels above this file).
        """
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent / 'ollama_config.json'
        return Path(__file__).parent.parent.parent / 'ollama_config.json'

    # Application directories
    TEMP_DIR = "temp"
    OUTPUT_DIR = "translate_rp"
    LOGS_DIR = "logs"
    RESOURCES_DIR = "resources"

    # UI theme colors
    COLORS = {
        "primary": "#5B8FF9",  # Main color (vibrant blue)
        "background": "#1E1E2E",  # Background color (dark)
        "card": "#2A2A3C",  # Card background (deeper color)
        "text": "#FFFFFF",  # Text color (white)
        "secondary": "#334656",  # Secondary color (for button backgrounds, etc.)
        "accent": "#6C7693",  # Accent color
        "divider": "#5B8FF9",  # Divider line
        "error": "#FF5555",  # Error display
    }

    # Translation settings
    MAX_TRANSLATION_RETRIES = 5
    TRANSLATION_RETRY_BASE_DELAY = 3

    # Ollama settings
    OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL = "mitmul/plamo-2-translate"

    def __init__(self):
        """Initialize configuration with default values."""
        self._pack_format: Optional[int] = None
        self._ollama_base_url: str = self.OLLAMA_DEFAULT_BASE_URL
        self._ollama_model: str = self.OLLAMA_DEFAULT_MODEL

    @property
    def pack_format(self) -> Optional[int]:
        """Get the current pack format.

        Returns:
            The current pack format or None if not set.
        """
        return self._pack_format

    @pack_format.setter
    def pack_format(self, value: Optional[int]):
        """Set the pack format.

        Args:
            value: The pack format to set, or None to unset it.
        """
        self._pack_format = value

    def get_pack_format_for_version(self, version: str) -> Optional[int]:
        """Get the pack format for a Minecraft version.

        Args:
            version: The Minecraft version string.

        Returns:
            The pack format or None if version not found.
        """
        return self.VERSION_TO_PACK_FORMAT.get(version)

    def get_app_version(self) -> str:
        """Get the application version from the package metadata.

        Returns:
            The version string used by the packaged application.
        """
        return __version__

    @property
    def OLLAMA_BASE_URL(self) -> str:
        """Get the Ollama server base URL."""
        return self._ollama_base_url

    @OLLAMA_BASE_URL.setter
    def OLLAMA_BASE_URL(self, value: str):
        """Set the Ollama server base URL."""
        self._ollama_base_url = value

    @property
    def OLLAMA_MODEL(self) -> str:
        """Get the Ollama model name."""
        return self._ollama_model

    @OLLAMA_MODEL.setter
    def OLLAMA_MODEL(self, value: str):
        """Set the Ollama model name."""
        self._ollama_model = value

    def save(self) -> None:
        """Write current Ollama settings to ollama_config.json."""
        path = self._config_file_path()
        try:
            data = {
                'ollama_base_url': self._ollama_base_url,
                'ollama_model': self._ollama_model,
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved Ollama config to {path}")
        except Exception as e:
            logger.warning(f"Failed to save Ollama config to {path}: {e}")


# Global config instance
config = Config()
