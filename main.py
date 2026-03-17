"""Entry point for the Minecraft MOD Translator Tool."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _configure_flet_view_path() -> None:
    """Set ``FLET_VIEW_PATH`` so Flet can locate its desktop client.

    In a Nuitka onefile build the ``flet_desktop`` package is compiled into
    the main binary while the Flet client files (``flet.exe`` and its DLLs)
    are extracted alongside it.  ``flet_desktop`` resolves the client path
    via ``Path(__file__).parent / "app"``, which may not match the actual
    extraction directory.  Setting ``FLET_VIEW_PATH`` before Flet is
    initialised provides a reliable fallback.
    """
    if os.environ.get("FLET_VIEW_PATH"):
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    flet_view_dir = os.path.join(base_dir, "flet_desktop", "app", "flet")
    if os.path.isdir(flet_view_dir):
        os.environ["FLET_VIEW_PATH"] = flet_view_dir


if getattr(sys, "frozen", False) or "__compiled__" in globals():
    _configure_flet_view_path()

from src.main import main

if __name__ == "__main__":
    main()
