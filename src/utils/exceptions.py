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
