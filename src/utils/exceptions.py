"""
Custom exceptions for the application.
"""


class MCMTException(Exception):
    """Base exception for all application-specific exceptions."""

    pass


class FileOperationError(MCMTException):
    """Exception raised for errors in file operations."""

    pass


class TranslationError(MCMTException):
    """Exception raised for errors in translation operations."""

    pass


class ResourcePackError(MCMTException):
    """Exception raised for errors in resource pack operations."""

    pass


class UIError(MCMTException):
    """Exception raised for errors in UI operations."""

    pass


class DependencyError(MCMTException):
    """Raised when an external dependency is missing or unusable.

    The Flet runtime requires certain system libraries (for example the
    ``libmpv`` shared object on Linux).  If one of these cannot be
    located we convert the low-level ``OSError`` into this more specific
    exception so that the caller can present a helpful message and
    terminate cleanly instead of dumping a stack trace.
    """

    pass
