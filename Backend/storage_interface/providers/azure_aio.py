"""Azure Blob using azure.storage.blob.aio (async SDK)."""

from __future__ import annotations

from typing import List, Optional

from ..base import ObjectInfo
from ..base_async import AsyncStorageProvider
from ..exceptions import ObjectNotFoundError, ProviderConfigError


def _ensure_container(connection_string: str, container: str) -> None:
    """One-time sync bootstrap so a container exists; avoids async __init__."""
    from azure.core.exceptions import ResourceExistsError  # type: ignore
    from azure.storage.blob import (  # type: ignore
        BlobServiceClient as SyncBlobServiceClient,
    )

    sc = SyncBlobServiceClient.from_connection_string(connection_string)
    try:
        sc.get_container_client(container).create_container()
    except ResourceExistsError:
        pass
    # container_client (async) is already bound to same path


class AzureAsyncBlobStorageProvider(AsyncStorageProvider):
    def __init__(self, container: str, connection_string: str) -> None:
        if not container:
            raise ProviderConfigError(
                "AZURE_BLOB_CONTAINER is required for Azure provider"
            )
        if not connection_string:
            raise ProviderConfigError(
                "AZURE_STORAGE_CONNECTION_STRING is required for Azure provider"
            )
        try:
            from azure.storage.blob.aio import BlobServiceClient  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise ProviderConfigError(
                "azure-storage-blob is required; install `azure-storage-blob`"
            ) from exc

        self._service = BlobServiceClient.from_connection_string(connection_string)
        self._container = self._service.get_container_client(container)
        _ensure_container(connection_string, container)

    async def aclose(self) -> None:
        await self._service.close()

    async def aput(
        self, key: str, value: bytes, content_type: Optional[str] = None
    ) -> None:
        from azure.storage.blob import ContentSettings  # type: ignore

        settings = ContentSettings(content_type=content_type) if content_type else None
        await self._container.upload_blob(
            name=key,
            data=value,
            overwrite=True,
            content_settings=settings,
        )

    async def aget(self, key: str) -> bytes:
        from azure.core.exceptions import ResourceNotFoundError  # type: ignore

        try:
            downloader = await self._container.download_blob(key)
            return await downloader.readall()
        except ResourceNotFoundError as exc:
            raise ObjectNotFoundError(key) from exc

    async def adelete(self, key: str) -> None:
        from azure.core.exceptions import ResourceNotFoundError  # type: ignore

        try:
            await self._container.delete_blob(key)
        except ResourceNotFoundError as exc:
            raise ObjectNotFoundError(key) from exc

    async def alist(self, prefix: str = "") -> List[ObjectInfo]:
        results: List[ObjectInfo] = []
        async for blob in self._container.list_blobs(name_starts_with=prefix or None):
            results.append(
                ObjectInfo(
                    key=blob.name,
                    size=blob.size,
                    last_modified=blob.last_modified.isoformat()
                    if blob.last_modified
                    else None,
                )
            )
        return results

    async def aexists(self, key: str) -> bool:
        return await self._container.get_blob_client(key).exists()
