"""Build the list of storage backends for unified HTTP API calls.

Unified mode targets **cloud object stores only** (S3, GCS, Azure Blob). Each
backend is included only when its env vars are set. Local filesystem is never
used for the HTTP object API (use `get_provider("local")` in Python for dev).

The HTTP layer enforces consistency for put/get/delete/head (see `app.py`).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from . import config
from .base import StorageProvider
from .factory import get_provider

if TYPE_CHECKING:
    from .base_async import AsyncStorageProvider

_UNIFIED_ORDER = ("s3", "gcs", "azure")


def _gcs_effective() -> bool:
    return bool(config.GCP_BUCKET)


def _azure_effective() -> bool:
    return bool(config.AZURE_CONTAINER and config.AZURE_CONNECTION_STRING)


def _s3_effective() -> bool:
    return bool(config.AWS_BUCKET)


def configured_unified_provider_ids() -> List[str]:
    """Return provider id strings that should participate in unified calls."""
    ids: List[str] = []
    for name in _UNIFIED_ORDER:
        if name == "s3" and not _s3_effective():
            continue
        if name == "gcs" and not _gcs_effective():
            continue
        if name == "azure" and not _azure_effective():
            continue
        ids.append(name)
    return ids


def get_unified_providers() -> List[Tuple[str, StorageProvider]]:
    """Return `(provider_id, provider)` for each configured unified backend (sync)."""
    return [(name, get_provider(name)) for name in configured_unified_provider_ids()]


def get_async_unified_providers() -> List[Tuple[str, AsyncStorageProvider]]:
    """Return `(provider_id, async_provider)` for unified routes (native async I/O)."""
    from .factory_async import get_async_provider

    return [
        (name, get_async_provider(name))
        for name in configured_unified_provider_ids()
    ]


def skip_reasons() -> dict:
    """Human-readable map of why each possible unified slot is off."""
    r = {}
    if not _s3_effective():
        r["s3"] = "AWS_S3_BUCKET not set"
    if not _gcs_effective():
        r["gcs"] = "GCP_GCS_BUCKET not set"
    if not _azure_effective():
        r["azure"] = "AZURE_BLOB_CONTAINER or AZURE_STORAGE_CONNECTION_STRING not set"
    r["local"] = (
        'not used in unified HTTP mode (clouds only); use get_provider("local") in code'
    )
    return r
