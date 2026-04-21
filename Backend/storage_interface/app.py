"""FastAPI wrapper around `StorageProvider` so any HTTP client (Postman,
curl, browser) can exercise the storage interface end-to-end.

Run locally:

    uvicorn Backend.storage_interface.app:app --reload --port 8100

The active provider is selected by `STORAGE_PROVIDER` (local|s3|gcs|azure)
or by the `?provider=` query parameter on each request.
"""

from __future__ import annotations

import base64
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .base import ObjectInfo
from .exceptions import ObjectNotFoundError, ProviderConfigError, StorageError
from .factory import get_provider

app = FastAPI(
    title="Momento Storage Interface",
    description="Cloud-agnostic storage API (put/get/delete/list) for Momento.",
    version="0.1.0",
)


class PutRequest(BaseModel):
    """Body for `PUT /objects/{key}` when sending JSON."""

    value_base64: Optional[str] = Field(
        None,
        description="Base64-encoded bytes. Use this for binary data.",
    )
    value_text: Optional[str] = Field(
        None,
        description="Plain text value. Ignored if `value_base64` is set.",
    )
    content_type: Optional[str] = None


class ObjectInfoModel(BaseModel):
    key: str
    size: Optional[int] = None
    last_modified: Optional[str] = None

    @classmethod
    def from_info(cls, info: ObjectInfo) -> "ObjectInfoModel":
        return cls(key=info.key, size=info.size, last_modified=info.last_modified)


class ListResponse(BaseModel):
    provider: str
    prefix: str
    count: int
    objects: List[ObjectInfoModel]


def _resolve_provider(name: Optional[str]):
    try:
        return get_provider(name), (name or "default")
    except ProviderConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/")
def root():
    """Service metadata and endpoint list."""
    return {
        "service": "Momento Storage Interface",
        "status": "ok",
        "endpoints": {
            "GET /health": "Liveness probe",
            "GET /providers": "Providers compiled in",
            "PUT /objects/{key}": "Upload JSON body or raw bytes",
            "GET /objects/{key}": "Download raw bytes",
            "DELETE /objects/{key}": "Remove a key",
            "GET /objects": "List keys under `prefix`",
            "HEAD /objects/{key}": "Existence check",
        },
        "query_params": {"provider": "local | s3 | gcs | azure (optional override)"},
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/providers")
def providers():
    return {"supported": ["local", "s3", "gcs", "azure"]}


@app.put("/objects/{key:path}")
async def put_object(
    key: str,
    request: Request,
    provider: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
):
    """Upload an object.

    Two modes:
    * `Content-Type: application/json` with a `PutRequest` body (good for
      Postman form-free testing).
    * Any other content type: the raw request body is stored as-is (good for
      binary uploads from curl / Postman `binary` body).
    """
    store, active = _resolve_provider(provider)
    ctype = request.headers.get("content-type", "").lower()

    try:
        if ctype.startswith("application/json"):
            payload = PutRequest(**(await request.json()))
            if payload.value_base64 is not None:
                try:
                    data = base64.b64decode(payload.value_base64, validate=True)
                except Exception as exc:
                    raise HTTPException(status_code=400, detail=f"invalid base64: {exc}")
            elif payload.value_text is not None:
                data = payload.value_text.encode("utf-8")
            else:
                raise HTTPException(
                    status_code=400,
                    detail="provide `value_base64` or `value_text`",
                )
            store.put(key, data, content_type=payload.content_type or content_type)
        else:
            data = await request.body()
            if not data:
                raise HTTPException(status_code=400, detail="empty request body")
            store.put(key, data, content_type=content_type or ctype or None)
    except StorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"ok": True, "provider": active, "key": key, "size": len(data)}


@app.get("/objects/{key:path}")
def get_object(key: str, provider: Optional[str] = Query(None)):
    """Download the bytes stored under `key`."""
    store, _ = _resolve_provider(provider)
    try:
        data = store.get(key)
    except ObjectNotFoundError:
        raise HTTPException(status_code=404, detail=f"not found: {key}")
    except StorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return Response(content=data, media_type="application/octet-stream")


@app.head("/objects/{key:path}")
def head_object(key: str, provider: Optional[str] = Query(None)):
    store, _ = _resolve_provider(provider)
    if not store.exists(key):
        raise HTTPException(status_code=404, detail="not found")
    return Response(status_code=200)


@app.delete("/objects/{key:path}")
def delete_object(key: str, provider: Optional[str] = Query(None)):
    store, active = _resolve_provider(provider)
    try:
        store.delete(key)
    except ObjectNotFoundError:
        raise HTTPException(status_code=404, detail=f"not found: {key}")
    except StorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"ok": True, "provider": active, "key": key}


@app.get("/objects", response_model=ListResponse)
def list_objects(
    prefix: str = Query("", description="Key prefix to filter by"),
    provider: Optional[str] = Query(None),
):
    store, active = _resolve_provider(provider)
    try:
        items = store.list(prefix)
    except StorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return ListResponse(
        provider=active,
        prefix=prefix,
        count=len(items),
        objects=[ObjectInfoModel.from_info(i) for i in items],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "Backend.storage_interface.app:app",
        host="0.0.0.0",
        port=8100,
        reload=True,
    )
