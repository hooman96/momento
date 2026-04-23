"""Factory for async `AsyncStorageProvider` instances (unified & native async I/O)."""

from __future__ import annotations

import threading
from typing import Optional

from . import config
from .base_async import AsyncStorageProvider
from .exceptions import ProviderConfigError

_cache: dict[str, AsyncStorageProvider] = {}
_lock = threading.Lock()


def _build_async(cache_key: str) -> AsyncStorageProvider:
    if cache_key == "s3":
        from .providers.s3_aio import S3AsyncStorageProvider

        return S3AsyncStorageProvider(
            bucket=config.AWS_BUCKET,
            region=config.AWS_REGION,
            access_key_id=config.AWS_ACCESS_KEY_ID or None,
            secret_access_key=config.AWS_SECRET_ACCESS_KEY or None,
        )
    if cache_key == "gcs":
        from .providers.gcs_aio import GCSAsyncStorageProvider

        return GCSAsyncStorageProvider(
            bucket=config.GCP_BUCKET,
            project=config.GCP_PROJECT or None,
        )
    if cache_key == "azure":
        from .providers.azure_aio import AzureAsyncBlobStorageProvider

        return AzureAsyncBlobStorageProvider(
            container=config.AZURE_CONTAINER,
            connection_string=config.AZURE_CONNECTION_STRING,
        )
    raise ProviderConfigError(f"unknown async storage cache key: {cache_key!r}")


def get_async_provider(name: Optional[str] = None) -> AsyncStorageProvider:
    """Return a cached async provider (one process-wide instance per cloud id)."""

    provider = (name or config.DEFAULT_PROVIDER).lower()

    if provider in ("s3", "aws"):
        key = "s3"
    elif provider in ("gcs", "gcp"):
        key = "gcs"
    elif provider == "azure":
        key = "azure"
    elif provider == "local":
        raise ProviderConfigError(
            "async provider is not used for local; unified mode is cloud-only"
        )
    else:
        raise ProviderConfigError(f"unknown async storage provider: {provider!r}")

    with _lock:
        if key not in _cache:
            _cache[key] = _build_async(key)
        return _cache[key]


async def aclose_all_async_providers() -> None:
    """Close aiohttp / transport sessions (GCS, Azure). Call from app lifespan shutdown."""
    with _lock:
        instances = list(_cache.values())
        _cache.clear()
    for inst in instances:
        fn = getattr(inst, "aclose", None)
        if fn is not None:
            await fn()  # type: ignore[misc]
