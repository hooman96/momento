"""AWS S3 backend (object storage)."""

from __future__ import annotations

from typing import List, Optional

from ..base import ObjectInfo, StorageProvider
from ..exceptions import ObjectNotFoundError, ProviderConfigError


class S3StorageProvider(StorageProvider):
    """`StorageProvider` backed by an AWS S3 bucket.

    Authentication follows the standard boto3 resolution order (env vars,
    shared credentials file, IAM role). An explicit key/secret can be passed
    in for local testing.
    """

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
            import boto3  # type: ignore
        except ImportError as exc:  # pragma: no cover - import guard
            raise ProviderConfigError(
                "boto3 is required for the S3 provider; install `boto3`"
            ) from exc

        self.bucket = bucket
        session_kwargs = {"region_name": region}
        if access_key_id and secret_access_key:
            session_kwargs["aws_access_key_id"] = access_key_id
            session_kwargs["aws_secret_access_key"] = secret_access_key
        self._client = boto3.client("s3", **session_kwargs)

    def put(self, key: str, value: bytes, content_type: Optional[str] = None) -> None:
        extra = {"ContentType": content_type} if content_type else {}
        self._client.put_object(Bucket=self.bucket, Key=key, Body=value, **extra)

    def get(self, key: str) -> bytes:
        from botocore.exceptions import ClientError  # type: ignore

        try:
            resp = self._client.get_object(Bucket=self.bucket, Key=key)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in ("NoSuchKey", "404"):
                raise ObjectNotFoundError(key) from exc
            raise
        return resp["Body"].read()

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)

    def list(self, prefix: str = "") -> List[ObjectInfo]:
        paginator = self._client.get_paginator("list_objects_v2")
        results: List[ObjectInfo] = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
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
        return results

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError  # type: ignore

        try:
            self._client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if code in ("NoSuchKey", "404", "NotFound") or status == 404:
                return False
            raise
