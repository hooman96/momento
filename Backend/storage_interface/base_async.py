"""Async variant of the storage contract for native async I/O (unified multi-cloud API)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .base import ObjectInfo
from .exceptions import ObjectNotFoundError


class AsyncStorageProvider(ABC):
    """Non-blocking object storage using vendor async clients (no thread-pool shim)."""

    @abstractmethod
    async def aput(
        self, key: str, value: bytes, content_type: Optional[str] = None
    ) -> None:
        """Store `value` under `key`."""

    @abstractmethod
    async def aget(self, key: str) -> bytes:
        """Return bytes for `key` or raise `ObjectNotFoundError`."""

    @abstractmethod
    async def adelete(self, key: str) -> None:
        """Remove `key` (raise `ObjectNotFoundError` if strict no-op not allowed)."""

    @abstractmethod
    async def alist(self, prefix: str = "") -> List[ObjectInfo]:
        """List objects whose key starts with `prefix`."""

    async def aexists(self, key: str) -> bool:
        """Default: existence via `aget`. Providers may override with HEAD-style calls."""
        try:
            await self.aget(key)
            return True
        except ObjectNotFoundError:
            return False
