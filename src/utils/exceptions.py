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
