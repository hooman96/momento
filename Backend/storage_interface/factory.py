"""Factory to pick a `StorageProvider` by name or from env config."""

from __future__ import annotations

from typing import Optional

from . import config
from .base import StorageProvider
from .exceptions import ProviderConfigError


def get_provider(name: Optional[str] = None) -> StorageProvider:
    """Return a configured `StorageProvider` instance.

    `name` overrides the `STORAGE_PROVIDER` env var. Supported values:
    `local`, `s3` (alias `aws`), `gcs` (alias `gcp`), `azure`.
    """

    provider = (name or config.DEFAULT_PROVIDER).lower()

    if provider == "local":
        from .providers.local import LocalStorageProvider

        return LocalStorageProvider(root=config.LOCAL_ROOT)

    if provider in ("s3", "aws"):
        from .providers.aws_s3 import S3StorageProvider

        return S3StorageProvider(
            bucket=config.AWS_BUCKET,
            region=config.AWS_REGION,
            access_key_id=config.AWS_ACCESS_KEY_ID or None,
            secret_access_key=config.AWS_SECRET_ACCESS_KEY or None,
        )

    if provider in ("gcs", "gcp"):
        from .providers.gcp_gcs import GCSStorageProvider

        return GCSStorageProvider(
            bucket=config.GCP_BUCKET,
            project=config.GCP_PROJECT or None,
        )

    if provider == "azure":
        from .providers.azure_blob import AzureBlobStorageProvider

        return AzureBlobStorageProvider(
            container=config.AZURE_CONTAINER,
            connection_string=config.AZURE_CONNECTION_STRING,
        )

    raise ProviderConfigError(f"unknown storage provider: {provider!r}")
