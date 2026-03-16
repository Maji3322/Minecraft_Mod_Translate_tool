"""Main entry point for the Minecraft MOD Translator Tool."""

import os
import sys

import flet as ft
import flet_desktop  # noqa: F401  # Keep desktop runtime visible to frozen builds.
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
        # verify that any external system requirements are satisfied
        from .utils.system import check_system_requirements

        # if a dependency is missing, the function will log an error and
        # raise an exception; handle it explicitly so we can exit cleanly
        try:
            check_system_requirements(logger)
        except Exception:  # pylint: disable=broad-except
            # the logger call above already recorded what went wrong
            sys.exit(1)

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
