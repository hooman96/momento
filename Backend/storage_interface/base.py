"""Abstract `StorageProvider` contract.

All concrete cloud backends (S3, GCS, Azure Blob, ...) implement this class.
The rest of the product depends only on this interface, not on any vendor SDK.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from .exceptions import ObjectNotFoundError


@dataclass
class ObjectInfo:
    """Lightweight metadata returned by `list`.

    Keeping this small and provider-agnostic. Providers may leave optional
    fields as `None` when the underlying service does not expose them.
    """

    key: str
    size: Optional[int] = None
    last_modified: Optional[str] = None  # ISO 8601 string


class StorageProvider(ABC):
    """Cloud-agnostic object/key-value storage contract.

    The contract is intentionally minimal so it maps cleanly onto object
    stores (S3, GCS, Azure Blob) and onto cache/KV stores (DynamoDB,
    Firestore, Cosmos DB) when needed.
    """

    @abstractmethod
    def put(self, key: str, value: bytes, content_type: Optional[str] = None) -> None:
        """Store `value` under `key`. Overwrites if the key exists."""

    @abstractmethod
    def get(self, key: str) -> bytes:
        """Return the bytes stored under `key`.

        Raises `ObjectNotFoundError` when the key is missing.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove `key`. No-op semantics when the key is already absent is
        acceptable; raise `ObjectNotFoundError` if strict delete is desired.
        """

    @abstractmethod
    def list(self, prefix: str = "") -> List[ObjectInfo]:
        """List objects whose key starts with `prefix`."""

    def exists(self, key: str) -> bool:
        """Default implementation that relies on `get`. Providers may
        override with a cheaper HEAD-style check."""
        try:
            self.get(key)
            return True
        except ObjectNotFoundError:
            return False
