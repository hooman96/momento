"""GCP GCS backend using gcloud-aio-storage (aiohttp, async I/O)."""

from __future__ import annotations

from typing import List, Optional

from ..base import ObjectInfo
from ..base_async import AsyncStorageProvider
from ..exceptions import ObjectNotFoundError, ProviderConfigError


def _is_not_found(exc: Exception) -> bool:
    st = getattr(exc, "status", None)
    if st == 404:
        return True
    msg = str(exc).lower()
    return "404" in msg or "not found" in msg


class GCSAsyncStorageProvider(AsyncStorageProvider):
    def __init__(self, bucket: str, project: Optional[str] = None):
        if not bucket:
            raise ProviderConfigError("GCP_GCS_BUCKET is required for GCS provider")
        try:
            from gcloud.aio.storage import Storage  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise ProviderConfigError(
                "gcloud-aio-storage is required for async GCS; install `gcloud-aio-storage`"
            ) from exc

        self._bucket = bucket
        self._project = project
        self._storage = Storage()
        # project is not passed to Storage(); ADC / GOOGLE_APPLICATION_CREDENTIALS used.

    async def aclose(self) -> None:
        await self._storage.close()

    async def aput(
        self, key: str, value: bytes, content_type: Optional[str] = None
    ) -> None:
        await self._storage.upload(
            self._bucket,
            key,
            value,
            content_type=content_type or "application/octet-stream",
        )

    async def aget(self, key: str) -> bytes:
        try:
            data = await self._storage.download(self._bucket, key)
            if isinstance(data, str):
                return data.encode("utf-8")
            return data
        except Exception as exc:
            if _is_not_found(exc):
                raise ObjectNotFoundError(key) from exc
            raise

    async def adelete(self, key: str) -> None:
        try:
            await self._storage.delete(self._bucket, key)
        except Exception as exc:
            if _is_not_found(exc):
                raise ObjectNotFoundError(key) from exc
            raise

    async def alist(self, prefix: str = "") -> List[ObjectInfo]:
        """GCS JSON API `list` — paginated with `pageToken` / `nextPageToken`."""
        results: List[ObjectInfo] = []
        params: dict = {"prefix": prefix} if prefix else {}
        while True:
            data = await self._storage.list_objects(self._bucket, params=params)
            for item in data.get("items", []) or []:
                name = item.get("name", "")
                size = item.get("size")
                if size is not None and isinstance(size, str):
                    try:
                        size = int(size)
                    except ValueError:
                        size = None
                results.append(
                    ObjectInfo(
                        key=name,
                        size=size,
                        last_modified=item.get("updated") or item.get("timeCreated"),
                    )
                )
            token = data.get("nextPageToken")
            if not token:
                break
            params = {**params, "pageToken": token}
        return results

    async def aexists(self, key: str) -> bool:
        try:
            await self._storage.download_metadata(self._bucket, key)
            return True
        except Exception as exc:
            if _is_not_found(exc):
                return False
            raise
