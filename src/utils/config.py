"""Configuration management for the application."""

import os
from typing import Dict, Optional

from dotenv import load_dotenv

from src import __version__

load_dotenv()


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

    # OpenRouter settings (class variables for defaults from env)
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    _env_api_key = os.getenv("OPENROUTER_API_KEY", "")

    def __init__(self):
        """Initialize configuration with default values."""
        self._pack_format: Optional[int] = None
        self._openrouter_api_key: str = self._env_api_key
        self._openrouter_model: str = ""
        self._fallback_models: list[str] = []

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
    def OPENROUTER_API_KEY(self) -> str:
        """Get the OpenRouter API key (in-memory only).

        Returns:
            The configured API key.
        """
        return self._openrouter_api_key

    @OPENROUTER_API_KEY.setter
    def OPENROUTER_API_KEY(self, value: str):
        """Set the OpenRouter API key (in-memory only).

        Args:
            value: The API key to set.
        """
        self._openrouter_api_key = value

    @property
    def OPENROUTER_MODEL(self) -> str:
        """Get the OpenRouter model.

        Returns:
            The configured model name.
        """
        return self._openrouter_model

    @OPENROUTER_MODEL.setter
    def OPENROUTER_MODEL(self, value: str):
        """Set the OpenRouter model.

        Args:
            value: The model name to set.
        """
        self._openrouter_model = value

    @property
    def FALLBACK_MODELS(self) -> list[str]:
        """Get the fallback models list.

        Returns:
            List of fallback model names.
        """
        return self._fallback_models

    @FALLBACK_MODELS.setter
    def FALLBACK_MODELS(self, value: list[str]):
        """Set the fallback models list.

        Args:
            value: List of model names to use as fallbacks.
        """
        self._fallback_models = value


# Global config instance
config = Config()
