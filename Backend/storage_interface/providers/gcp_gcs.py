"""Google Cloud Storage backend (object storage)."""

from __future__ import annotations

from typing import List, Optional

from ..base import ObjectInfo, StorageProvider
from ..exceptions import ObjectNotFoundError, ProviderConfigError


class GCSStorageProvider(StorageProvider):
    """`StorageProvider` backed by a Google Cloud Storage bucket.

    Uses Application Default Credentials by default. Set
    `GOOGLE_APPLICATION_CREDENTIALS` to a service-account JSON path to
    authenticate from a local machine.
    """

    def __init__(self, bucket: str, project: Optional[str] = None):
        if not bucket:
            raise ProviderConfigError("GCP_GCS_BUCKET is required for GCS provider")
        try:
            from google.cloud import storage  # type: ignore
        except ImportError as exc:  # pragma: no cover - import guard
            raise ProviderConfigError(
                "google-cloud-storage is required; install `google-cloud-storage`"
            ) from exc

        self._client = storage.Client(project=project) if project else storage.Client()
        self._bucket = self._client.bucket(bucket)
        self.bucket_name = bucket

    def put(self, key: str, value: bytes, content_type: Optional[str] = None) -> None:
        blob = self._bucket.blob(key)
        blob.upload_from_string(
            value,
            content_type=content_type or "application/octet-stream",
        )

    def get(self, key: str) -> bytes:
        from google.cloud.exceptions import NotFound  # type: ignore

        blob = self._bucket.blob(key)
        try:
            return blob.download_as_bytes()
        except NotFound as exc:
            raise ObjectNotFoundError(key) from exc

    def delete(self, key: str) -> None:
        from google.cloud.exceptions import NotFound  # type: ignore

        blob = self._bucket.blob(key)
        try:
            blob.delete()
        except NotFound as exc:
            raise ObjectNotFoundError(key) from exc

    def list(self, prefix: str = "") -> List[ObjectInfo]:
        results: List[ObjectInfo] = []
        for blob in self._client.list_blobs(self._bucket, prefix=prefix):
            results.append(
                ObjectInfo(
                    key=blob.name,
                    size=blob.size,
                    last_modified=blob.updated.isoformat() if blob.updated else None,
                )
            )
        return results

    def exists(self, key: str) -> bool:
        return self._bucket.blob(key).exists(self._client)
