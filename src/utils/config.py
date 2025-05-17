"""
Configuration management for the application.
"""

from typing import Dict, Optional


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
        "1.21.4": 46,
    }
    
    # Application directories
    TEMP_DIR = "temp"
    OUTPUT_DIR = "translate_rp"
    LOGS_DIR = "logs"
    RESOURCES_DIR = "resources"
    
    # UI theme colors
    COLORS = {
        "primary": "#5B8FF9",      # Main color (vibrant blue)
        "background": "#1E1E2E",   # Background color (dark)
        "card": "#2A2A3C",         # Card background (deeper color)
        "text": "#FFFFFF",         # Text color (white)
        "secondary": "#334656",    # Secondary color (for button backgrounds, etc.)
        "accent": "#6C7693",       # Accent color
        "divider": "#5B8FF9",      # Divider line
        "error": "#FF5555",        # Error display
    }
    
    # Translation settings
    MAX_TRANSLATION_RETRIES = 5
    TRANSLATION_RETRY_BASE_DELAY = 3
    
    def __init__(self):
        self._pack_format: Optional[int] = None
        
    @property
    def pack_format(self) -> Optional[int]:
        """Get the current pack format."""
        return self._pack_format
        
    @pack_format.setter
    def pack_format(self, value: int):
        """Set the pack format."""
        self._pack_format = value
        
    def get_pack_format_for_version(self, version: str) -> Optional[int]:
        """Get the pack format for a Minecraft version."""
        return self.VERSION_TO_PACK_FORMAT.get(version)


# Create a global config instance
config = Config()