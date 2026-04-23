"""Azure Blob Storage backend (object storage)."""

from __future__ import annotations

from typing import List, Optional

from ..base import ObjectInfo, StorageProvider
from ..exceptions import ObjectNotFoundError, ProviderConfigError


class AzureBlobStorageProvider(StorageProvider):
    """`StorageProvider` backed by an Azure Blob Storage container.

    Uses a connection string for simplicity. For production consider
    `DefaultAzureCredential`; that can be swapped in without changing the
    public interface.
    """

    def __init__(self, container: str, connection_string: str):
        if not container:
            raise ProviderConfigError(
                "AZURE_BLOB_CONTAINER is required for Azure provider"
            )
        if not connection_string:
            raise ProviderConfigError(
                "AZURE_STORAGE_CONNECTION_STRING is required for Azure provider"
            )
        try:
            from azure.storage.blob import BlobServiceClient  # type: ignore
            from azure.core.exceptions import ResourceExistsError  # type: ignore
        except ImportError as exc:  # pragma: no cover - import guard
            raise ProviderConfigError(
                "azure-storage-blob is required; install `azure-storage-blob`"
            ) from exc

        self._service = BlobServiceClient.from_connection_string(connection_string)
        self._container = self._service.get_container_client(container)
        try:
            self._container.create_container()
        except ResourceExistsError:
            # Container already exists; no setup action needed.
            pass

    def put(self, key: str, value: bytes, content_type: Optional[str] = None) -> None:
        from azure.storage.blob import ContentSettings  # type: ignore

        settings = ContentSettings(content_type=content_type) if content_type else None
        self._container.upload_blob(
            name=key,
            data=value,
            overwrite=True,
            content_settings=settings,
        )

    def get(self, key: str) -> bytes:
        from azure.core.exceptions import ResourceNotFoundError  # type: ignore

        try:
            downloader = self._container.download_blob(key)
            return downloader.readall()
        except ResourceNotFoundError as exc:
            raise ObjectNotFoundError(key) from exc

    def delete(self, key: str) -> None:
        from azure.core.exceptions import ResourceNotFoundError  # type: ignore

        try:
            self._container.delete_blob(key)
        except ResourceNotFoundError as exc:
            raise ObjectNotFoundError(key) from exc

    def list(self, prefix: str = "") -> List[ObjectInfo]:
        results: List[ObjectInfo] = []
        for blob in self._container.list_blobs(name_starts_with=prefix or None):
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

    def exists(self, key: str) -> bool:
        return self._container.get_blob_client(key).exists()
