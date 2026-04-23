"""AWS S3 backend using aioboto3 (async HTTP via aiobotocore)."""

from __future__ import annotations

from typing import List, Optional

from ..base import ObjectInfo
from ..base_async import AsyncStorageProvider
from ..exceptions import ObjectNotFoundError, ProviderConfigError


class S3AsyncStorageProvider(AsyncStorageProvider):
    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
    ):
        if not bucket:
            raise ProviderConfigError("AWS_S3_BUCKET is required for S3 provider")
        try:
            import aioboto3  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise ProviderConfigError(
                "aioboto3 is required for async S3; install `aioboto3`"
            ) from exc

        self.bucket = bucket
        self._region = region
        if access_key_id and secret_access_key:
            self._session = aioboto3.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
            )
        else:
            self._session = aioboto3.Session()

    async def aclose(self) -> None:
        """No long-lived aiohttp client on the session; hook exists for symmetry."""
        return None

    async def aput(
        self, key: str, value: bytes, content_type: Optional[str] = None
    ) -> None:
        kwargs: dict = {"Bucket": self.bucket, "Key": key, "Body": value}
        if content_type:
            kwargs["ContentType"] = content_type
        async with self._session.client("s3", region_name=self._region) as client:
            await client.put_object(**kwargs)

    async def aget(self, key: str) -> bytes:
        from botocore.exceptions import ClientError  # type: ignore

        try:
            async with self._session.client("s3", region_name=self._region) as client:
                resp = await client.get_object(Bucket=self.bucket, Key=key)
                body = resp["Body"]
                data = await body.read()
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in ("NoSuchKey", "404"):
                raise ObjectNotFoundError(key) from exc
            raise
        return data

    async def adelete(self, key: str) -> None:
        from botocore.exceptions import ClientError  # type: ignore

        try:
            async with self._session.client("s3", region_name=self._region) as client:
                await client.delete_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in ("NoSuchKey", "404"):
                raise ObjectNotFoundError(key) from exc
            raise

    async def alist(self, prefix: str = "") -> List[ObjectInfo]:
        results: List[ObjectInfo] = []
        async with self._session.client("s3", region_name=self._region) as client:
            token: Optional[str] = None
            while True:
                kwargs: dict = {"Bucket": self.bucket, "Prefix": prefix}
                if token:
                    kwargs["ContinuationToken"] = token
                page = await client.list_objects_v2(**kwargs)
                for obj in page.get("Contents", []) or []:
                    results.append(
                        ObjectInfo(
                            key=obj["Key"],
                            size=obj.get("Size"),
                            last_modified=obj["LastModified"].isoformat()
                            if obj.get("LastModified")
                            else None,
                        )
                    )
                if not page.get("IsTruncated"):
                    break
                token = page.get("NextContinuationToken")
        return results

    async def aexists(self, key: str) -> bool:
        from botocore.exceptions import ClientError  # type: ignore

        try:
            async with self._session.client("s3", region_name=self._region) as client:
                await client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if code in ("NoSuchKey", "404", "NotFound") or status == 404:
                return False
            raise
