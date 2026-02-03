"""Main entry point for the Minecraft MOD Translator Tool."""

import os
import sys

import flet as ft
from flet import AppView

from .ui.app import start_app
from .utils.logging import setup_root_logger


def main():
    """Main entry point for the application."""
    logger = setup_root_logger()
    logger.info("Starting Minecraft MOD Translator Tool")

    sys.excepthook = lambda exc_type, exc_value, exc_tb: logger.exception(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_tb)
    )

    resources_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources"
    )

    try:
        ft.app(
            target=start_app,
            view=AppView.FLET_APP,
            assets_dir=resources_dir,
        )
    except Exception:
        logger.exception("Unhandled exception when running Flet app")
        raise


if __name__ == "__main__":
    main()
