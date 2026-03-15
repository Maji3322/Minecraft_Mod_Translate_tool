"""Helpers for validating the runtime environment.

This module is intentionally small; at the moment the only requirement we
need to verify is the presence of ``libmpv`` on Linux.  Future checks
(e.g. Python version, network connectivity) can live here as well.
"""

import ctypes
import logging
import sys

from .exceptions import DependencyError


def ensure_libmpv(logger: logging.Logger) -> None:
    """Validate that :pacakge:`libmpv` is loadable.

    The ``flet`` binary distributed by PyPI relies on the MPV library for
    handling media.  On Linux this is provided by a system package (e.g.
    ``libmpv1`` on Debian/Ubuntu or ``mpv-libs`` on Fedora).  If the
    shared object cannot be loaded the Flet executable will terminate with a
    confusing linker error; calling this function early allows us to give a
    clear, actionable message instead.

    Args:
        logger: a logger instance on which to emit diagnostics.

    Raises:
        DependencyError: if the library cannot be loaded.
    """

    # only check on Linux; other platforms bundle or do not require libmpv
    if not sys.platform.startswith("linux"):
        return

    try:
        ctypes.CDLL("libmpv.so.1")
    except OSError as exc:
        msg = (
            "required shared library 'libmpv.so.1' not found; "
            "please install it using your package manager (e.g. 'sudo apt "
            "install libmpv1' on Debian/Ubuntu, 'sudo dnf install mpv-libs' "
            "on Fedora/CentOS).")
        logger.error(msg)
        raise DependencyError(msg) from exc


def check_system_requirements(logger: logging.Logger) -> None:
    """Run all platform-specific sanity checks.

    Currently this is just a thin wrapper around :func:`ensure_libmpv`, but
    the indirection makes it easy to add additional validators later.
    """

    ensure_libmpv(logger)

