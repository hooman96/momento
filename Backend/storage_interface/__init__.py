"""Cloud-agnostic storage interface for Momento backend.

Exposes a small `StorageProvider` contract (put/get/delete/list) that the rest
of the product uses, plus concrete implementations for AWS S3, GCP GCS, Azure
Blob Storage, and a Local filesystem backend for development. The FastAPI
HTTP wrapper (`app.py`) uses unified multi-cloud I/O only; use `get_provider`
here for single-backend or local tests.
"""

from .base import StorageProvider, ObjectInfo
from .exceptions import (
    StorageError,
    ObjectNotFoundError,
    ProviderConfigError,
)
from .factory import get_provider

__all__ = [
    "StorageProvider",
    "ObjectInfo",
    "StorageError",
    "ObjectNotFoundError",
    "ProviderConfigError",
    "get_provider",
]
