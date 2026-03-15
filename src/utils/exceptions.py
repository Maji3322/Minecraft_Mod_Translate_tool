"""Custom exceptions for the application."""


class MCMTException(Exception):
    """Base exception for all application-specific exceptions."""


class FileOperationError(MCMTException):
    """Exception raised for errors in file operations."""


class TranslationError(MCMTException):
    """Exception raised for errors in translation operations."""


class ResourcePackError(MCMTException):
    """Exception raised for errors in resource pack operations."""


class UIError(MCMTException):
    """Exception raised for errors in UI operations."""


class DependencyError(MCMTException):
    """Raised when an external dependency is missing or unusable.

    The Flet runtime requires certain system libraries (for example the
    ``libmpv`` shared object on Linux).  If one of these cannot be
    located we convert the low-level ``OSError`` into this more specific
    exception so that the caller can present a helpful message and
    terminate cleanly instead of dumping a stack trace.
    """
