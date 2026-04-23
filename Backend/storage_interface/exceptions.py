"""Exception hierarchy for the storage interface."""


class StorageError(Exception):
    """Base class for all storage-related errors."""


class ObjectNotFoundError(StorageError):
    """Raised by `get`/`delete` when the key does not exist."""


class ProviderConfigError(StorageError):
    """Raised when a provider is missing required configuration."""
