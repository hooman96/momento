"""FastAPI wrapper around `StorageProvider` so any HTTP client (Postman,
curl, browser) can exercise the storage interface end-to-end.

Run locally:

    uvicorn Backend.storage_interface.app:app --reload --port 8100

`PUT/GET/DELETE/HEAD /objects/{key}` always run against **every** configured
cloud (S3, GCS, Azure) in parallel — there is no per-provider HTTP override, so
writes and reads cannot accidentally target a single backend. Unified I/O uses
**native async** clients (`aioboto3`, `gcloud-aio-storage`,
`azure.storage.blob.aio`) with `asyncio.gather` (no `asyncio.to_thread` on
those paths). For local or single-cloud testing, use `get_provider()` from
Python code (`factory.py`), not this HTTP API.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, List, Optional, Tuple

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from .base import ObjectInfo
from .exceptions import ObjectNotFoundError
from .factory_async import aclose_all_async_providers
from . import unified

logger = logging.getLogger("momento.storage_interface")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await aclose_all_async_providers()


app = FastAPI(
    title="Momento Storage Interface",
    description="Cloud-agnostic storage API (put/get/delete/list) for Momento.",
    version="0.1.0",
    lifespan=lifespan,
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


async def _read_put_body(
    request: Request, content_type_query: Optional[str]
) -> tuple[bytes, Optional[str]]:
    """Parse raw or JSON body for PUT endpoints. Returns (bytes, content_type)."""
    ctype = request.headers.get("content-type", "").lower()

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
        final_ct = payload.content_type or content_type_query
        return data, final_ct

    data = await request.body()
    if not data:
        raise HTTPException(status_code=400, detail="empty request body")
    final_ct = content_type_query or ctype or None
    return data, final_ct


def _log_unified(msg: str) -> None:
    print(msg, flush=True)
    logger.info(msg)


def _exc_detail(exc: BaseException) -> str:
    """Stable string for logs and JSON when vendor SDKs raise outside StorageError."""
    return f"{type(exc).__name__}: {exc}"


async def _rollback_unified_puts(
    key: str, committed: List[Tuple[str, Any]], per_results: dict
) -> None:
    """Best-effort parallel `adelete` after a failed unified PUT so spaces do not diverge."""

    async def _one(name: str, store: Any) -> None:
        rb_t = time.perf_counter()
        try:
            await store.adelete(key)
            per_results[name]["rolled_back"] = True
            per_results[name]["rollback_ms"] = round(
                (time.perf_counter() - rb_t) * 1000, 2
            )
        except ObjectNotFoundError:
            per_results[name]["rolled_back"] = True
            per_results[name]["rollback_ms"] = round(
                (time.perf_counter() - rb_t) * 1000, 2
            )
        except Exception as exc:
            per_results[name]["rolled_back"] = False
            per_results[name]["rollback_error"] = _exc_detail(exc)

    await asyncio.gather(*[_one(name, store) for name, store in committed])


@app.get("/")
def root():
    """Service metadata and endpoint list."""
    return {
        "service": "Momento Storage Interface",
        "status": "ok",
        "endpoints": {
            "GET /health": "Liveness probe",
            "GET /providers": "Which cloud ids are configured for unified I/O",
            "PUT /objects/{key}": "Upload to every configured cloud (JSON or raw body)",
            "GET /objects/{key}": "Download after verifying every cloud has identical bytes",
            "DELETE /objects/{key}": "Delete on every configured cloud",
            "GET /objects": "Unified list across clouds, or `?unified_status=1` for config only",
            "HEAD /objects/{key}": "200 only if the key exists on every configured cloud",
        },
        "query_params": {
            "unified_status": "on GET /objects (no key in path): `1` returns which clouds are in the unified set",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/providers")
def providers():
    """Configured unified backends (HTTP API is unified-only for object keys)."""
    return {
        "unified_includes": unified.configured_unified_provider_ids(),
        "skips": unified.skip_reasons(),
        "note": "Single-provider HTTP access was removed; use `get_provider()` in Python for local tests.",
    }


@app.put("/objects/{key:path}")
async def put_object(
    key: str,
    request: Request,
    content_type: Optional[str] = Query(None),
):
    """Upload the same object to every configured cloud (rollback on partial failure).

    * `Content-Type: application/json` with a `PutRequest` body (Postman-friendly).
    * Any other content type: raw body bytes (curl / Postman binary).
    """
    pairs = _unified_async_backends_or_503()
    t0 = time.perf_counter()
    data, ct = await _read_put_body(request, content_type)

    async def _put_one(name: str, store: Any) -> Tuple[str, dict]:
        t1 = time.perf_counter()
        try:
            await store.aput(key, data, content_type=ct)
            elapsed = round((time.perf_counter() - t1) * 1000, 2)
            return name, {
                "ok": True,
                "elapsed_ms": elapsed,
                "error": None,
                "rolled_back": False,
            }
        except Exception as exc:
            elapsed = round((time.perf_counter() - t1) * 1000, 2)
            return name, {
                "ok": False,
                "elapsed_ms": elapsed,
                "error": _exc_detail(exc),
            }

    put_rows = await asyncio.gather(*[_put_one(n, s) for n, s in pairs])
    per_results = dict(put_rows)
    all_put_ok = all(v.get("ok") for v in per_results.values())
    if not all_put_ok:
        committed = [(n, s) for n, s in pairs if per_results[n]["ok"]]
        await _rollback_unified_puts(key, committed, per_results)
    e2e_ms = round((time.perf_counter() - t0) * 1000, 2)
    per_ms_only = {k: v["elapsed_ms"] for k, v in per_results.items()}
    max_ms = max(per_ms_only.values()) if per_ms_only else 0.0
    _log_unified(
        f"[unified] PUT key={key!r} e2e_ms={e2e_ms} parallel_max_provider_ms={max_ms} "
        f"per_provider_ms={per_ms_only!r} "
        f"errors={[k for k, v in per_results.items() if not v.get('ok')]!r}"
    )
    all_ok = all_put_ok
    body: dict = {
        "ok": all_ok,
        "key": key,
        "unified": True,
        "parallel": True,
        "async_io": True,
        "size": len(data),
        "elapsed_ms": e2e_ms,
        "max_provider_ms": max_ms,
        "providers": per_results,
    }
    return JSONResponse(status_code=200 if all_ok else 502, content=body)


def _unified_async_backends_or_503() -> list:
    """Native async clients for S3, GCS, and Azure (see `factory_async`)."""
    pairs = unified.get_async_unified_providers()
    if not pairs:
        raise HTTPException(
            status_code=503,
            detail=(
                "No cloud backends configured for unified API. Set at least one of: "
                "AWS_S3_BUCKET (+ credentials), GCP_GCS_BUCKET (+ GCP_PROJECT / ADC), "
                "AZURE_BLOB_CONTAINER + AZURE_STORAGE_CONNECTION_STRING. "
                "Install async dependencies: `aioboto3`, `gcloud-aio-storage` (see requirements.txt)."
            ),
        )
    return pairs


@app.get("/objects/{key:path}")
async def get_object(key: str):
    """Download bytes after reading every configured cloud and verifying they match."""
    pairs = _unified_async_backends_or_503()
    t0 = time.perf_counter()

    async def _get_one(name: str, store: Any) -> Tuple[str, str, Any, float]:
        t1 = time.perf_counter()
        try:
            b = await store.aget(key)
            ms = round((time.perf_counter() - t1) * 1000, 2)
            return name, "ok", b, ms
        except ObjectNotFoundError:
            ms = round((time.perf_counter() - t1) * 1000, 2)
            return name, "not_found", None, ms
        except Exception as exc:
            ms = round((time.perf_counter() - t1) * 1000, 2)
            return name, "error", _exc_detail(exc), ms

    rows = await asyncio.gather(*[_get_one(n, s) for n, s in pairs])
    per_try: list = []
    blobs: List[Tuple[str, bytes]] = []
    for name, status, extra, ms in rows:
        if status == "ok":
            per_try.append({"provider": name, "result": "ok", "elapsed_ms": ms})
            blobs.append((name, extra))
        elif status == "not_found":
            per_try.append({"provider": name, "result": "not_found", "elapsed_ms": ms})
        else:
            per_try.append(
                {
                    "provider": name,
                    "result": "error",
                    "error": str(extra),
                    "elapsed_ms": ms,
                }
            )
    e2e_ms = round((time.perf_counter() - t0) * 1000, 2)
    errs = [p for p in per_try if p.get("result") == "error"]
    if errs:
        _log_unified(
            f"[unified] GET key={key!r} e2e_ms={e2e_ms} transport_errors={errs!r}"
        )
        raise HTTPException(
            status_code=502,
            detail={
                "message": "unified GET failed on one or more backends",
                "unified": True,
                "async_io": True,
                "providers": per_try,
                "e2e_ms": e2e_ms,
            },
        )
    if not blobs:
        _log_unified(
            f"[unified] GET key={key!r} e2e_ms={e2e_ms} not_found on all providers={per_try!r}"
        )
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"not found: {key}",
                "unified": True,
                "async_io": True,
                "providers": per_try,
                "e2e_ms": e2e_ms,
            },
        )
    if len(blobs) < len(pairs):
        _log_unified(
            f"[unified] GET key={key!r} e2e_ms={e2e_ms} drift_missing_on_some={per_try!r}"
        )
        raise HTTPException(
            status_code=409,
            detail={
                "message": "unified drift: object missing on one or more backends",
                "unified": True,
                "async_io": True,
                "providers": per_try,
                "e2e_ms": e2e_ms,
            },
        )
    ref = blobs[0][1]
    for _name, b in blobs[1:]:
        if b != ref:
            sizes = {n: len(x) for n, x in blobs}
            _log_unified(
                f"[unified] GET key={key!r} e2e_ms={e2e_ms} byte_mismatch sizes={sizes!r}"
            )
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "unified drift: same key has different bytes across backends",
                    "unified": True,
                    "async_io": True,
                    "providers": per_try,
                    "sizes_by_provider": sizes,
                    "e2e_ms": e2e_ms,
                },
            )
    max_ms = max(p["elapsed_ms"] for p in per_try) if per_try else 0.0
    _log_unified(
        f"[unified] GET key={key!r} e2e_ms={e2e_ms} parallel_max_provider_ms={max_ms} "
        f"verified={len(blobs)} backends same_bytes_len={len(ref)} "
        f"per_provider_ms={[p['elapsed_ms'] for p in per_try]!r}"
    )
    hdr = {
        "X-Unified-Verified-Count": str(len(blobs)),
        "X-Unified-Elapsed-Ms": str(e2e_ms),
        "X-Unified-Async-IO": "true",
    }
    return Response(
        content=ref,
        media_type="application/octet-stream",
        headers=hdr,
    )


@app.head("/objects/{key:path}")
async def head_object(key: str):
    """200 only when the key exists on every configured cloud (checked in parallel)."""
    pairs = _unified_async_backends_or_503()
    t0 = time.perf_counter()

    async def _head_one(name: str, store: Any) -> Tuple[str, str, Any, float]:
        t1 = time.perf_counter()
        try:
            exists = await store.aexists(key)
            ms = round((time.perf_counter() - t1) * 1000, 2)
            return name, "ok", exists, ms
        except Exception as exc:
            ms = round((time.perf_counter() - t1) * 1000, 2)
            return name, "error", _exc_detail(exc), ms

    rows = await asyncio.gather(*[_head_one(n, s) for n, s in pairs])
    flags: list = []
    for name, kind, payload, ms in rows:
        if kind == "ok":
            flags.append({"provider": name, "exists": payload, "elapsed_ms": ms})
        else:
            flags.append(
                {
                    "provider": name,
                    "result": "error",
                    "error": str(payload),
                    "elapsed_ms": ms,
                }
            )
    head_errs = [f for f in flags if f.get("result") == "error"]
    if head_errs:
        e2e_ms = round((time.perf_counter() - t0) * 1000, 2)
        _log_unified(
            f"[unified] HEAD key={key!r} e2e_ms={e2e_ms} transport_errors={head_errs!r}"
        )
        raise HTTPException(
            status_code=502,
            detail={
                "message": "unified HEAD failed on one or more backends",
                "unified": True,
                "async_io": True,
                "providers": flags,
                "e2e_ms": e2e_ms,
            },
        )
    n_ok = sum(1 for f in flags if f.get("exists") is True)
    total = len(flags)
    e2e_ms = round((time.perf_counter() - t0) * 1000, 2)
    max_ms = max(f["elapsed_ms"] for f in flags) if flags else 0.0
    if n_ok == total:
        _log_unified(
            f"[unified] HEAD key={key!r} e2e_ms={e2e_ms} parallel_max_provider_ms={max_ms} "
            f"all_present={total}/{total}"
        )
        return Response(
            status_code=200,
            headers={
                "X-Unified-Backends-Ready": f"{n_ok}/{total}",
                "X-Unified-Elapsed-Ms": str(e2e_ms),
                "X-Unified-Async-IO": "true",
            },
        )
    if n_ok == 0:
        _log_unified(
            f"[unified] HEAD key={key!r} e2e_ms={e2e_ms} absent_all flags={flags!r}"
        )
        raise HTTPException(
            status_code=404,
            detail={
                "message": "not found",
                "unified": True,
                "async_io": True,
                "providers": flags,
            },
        )
    _log_unified(
        f"[unified] HEAD key={key!r} e2e_ms={e2e_ms} drift_ready={n_ok}/{total} flags={flags!r}"
    )
    raise HTTPException(
        status_code=409,
        detail={
            "message": "unified drift: key exists on some backends but not all",
            "unified": True,
            "async_io": True,
            "providers": flags,
            "e2e_ms": e2e_ms,
        },
    )


@app.delete("/objects/{key:path}")
async def delete_object(key: str):
    """Delete on every configured cloud backend in parallel."""
    pairs = _unified_async_backends_or_503()
    t0 = time.perf_counter()

    async def _del_one(name: str, store: Any) -> Tuple[str, dict]:
        t1 = time.perf_counter()
        try:
            await store.adelete(key)
            elapsed = round((time.perf_counter() - t1) * 1000, 2)
            return name, {
                "ok": True,
                "elapsed_ms": elapsed,
                "error": None,
            }
        except ObjectNotFoundError:
            elapsed = round((time.perf_counter() - t1) * 1000, 2)
            return name, {
                "ok": True,
                "elapsed_ms": elapsed,
                "error": None,
                "note": "not_found (idempotent delete)",
            }
        except Exception as exc:
            elapsed = round((time.perf_counter() - t1) * 1000, 2)
            return name, {
                "ok": False,
                "elapsed_ms": elapsed,
                "error": _exc_detail(exc),
            }

    del_rows = await asyncio.gather(*[_del_one(n, s) for n, s in pairs])
    per_results = dict(del_rows)
    e2e_ms = round((time.perf_counter() - t0) * 1000, 2)
    per_ms_only = {k: v["elapsed_ms"] for k, v in per_results.items()}
    max_ms = max(per_ms_only.values()) if per_ms_only else 0.0
    _log_unified(
        f"[unified] DELETE key={key!r} e2e_ms={e2e_ms} parallel_max_provider_ms={max_ms} "
        f"per_provider_ms={per_ms_only!r} "
        f"errors={[k for k, v in per_results.items() if not v.get('ok')]!r}"
    )
    any_fail = any(not v.get("ok") for v in per_results.values())
    body: dict = {
        "ok": not any_fail,
        "unified": True,
        "parallel": True,
        "async_io": True,
        "key": key,
        "elapsed_ms": e2e_ms,
        "max_provider_ms": max_ms,
        "providers": per_results,
    }
    return JSONResponse(status_code=200 if not any_fail else 502, content=body)


@app.get("/objects")
async def list_objects(
    prefix: str = Query("", description="Key prefix to filter by"),
    unified_status: bool = Query(
        False,
        description="If true, return which backends participate in unified I/O (omit `prefix`).",
    ),
):
    if unified_status:
        if prefix:
            raise HTTPException(
                status_code=400,
                detail="Omit `prefix` when `unified_status=1`",
            )
        return {
            "unified_includes": unified.configured_unified_provider_ids(),
            "skips": unified.skip_reasons(),
        }

    pairs = _unified_async_backends_or_503()
    t0 = time.perf_counter()

    async def _list_one(name: str, store: Any) -> Tuple[str, str, Any, float]:
        t1 = time.perf_counter()
        try:
            items = await store.alist(prefix)
            ms = round((time.perf_counter() - t1) * 1000, 2)
            return name, "ok", items, ms
        except Exception as exc:
            ms = round((time.perf_counter() - t1) * 1000, 2)
            return name, "error", _exc_detail(exc), ms

    rows = await asyncio.gather(*[_list_one(n, s) for n, s in pairs])
    per_try: list = []
    by_key: dict[str, ObjectInfo] = {}
    order: List[str] = []
    for name, kind, payload, ms in rows:
        if kind == "ok":
            per_try.append({"provider": name, "result": "ok", "elapsed_ms": ms})
            for info in payload:
                if info.key not in by_key:
                    by_key[info.key] = info
                    order.append(info.key)
        else:
            per_try.append(
                {
                    "provider": name,
                    "result": "error",
                    "error": str(payload),
                    "elapsed_ms": ms,
                }
            )
    errs = [p for p in per_try if p.get("result") == "error"]
    if errs:
        e2e_ms = round((time.perf_counter() - t0) * 1000, 2)
        raise HTTPException(
            status_code=502,
            detail={
                "message": "unified LIST failed on one or more backends",
                "unified": True,
                "async_io": True,
                "providers": per_try,
                "e2e_ms": e2e_ms,
            },
        )
    e2e_ms = round((time.perf_counter() - t0) * 1000, 2)
    merged = [by_key[k] for k in order]
    return {
        "unified": True,
        "async_io": True,
        "prefix": prefix,
        "count": len(merged),
        "objects": [ObjectInfoModel.from_info(i).model_dump() for i in merged],
        "elapsed_ms": e2e_ms,
        "providers": per_try,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "Backend.storage_interface.app:app",
        host="0.0.0.0",
        port=8100,
        reload=True,
    )
