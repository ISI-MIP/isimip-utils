"""Custom exceptions for ISIMIP tools."""


class ExtractionError(RuntimeError):
    """Raised when data extraction operations fail."""
    pass


class ValidationError(RuntimeError):
    """Raised when data validation fails."""
    pass


class DidNotMatch(RuntimeError):
    """Raised when a pattern does not match the expected format."""
    pass


class NotFound(RuntimeError):
    """Raised when a required resource or file is not found."""
    pass


class ConfigError(RuntimeError):
    """Raised when there is an error in configuration."""
    pass
