# Storage Interface

Cloud-agnostic storage layer for the Momento backend. The rest of the product
depends on a single abstract class, `StorageProvider`, and never imports a
vendor SDK directly. Concrete backends exist for AWS S3, GCP GCS, Azure Blob,
and a local filesystem (used for development and unit tests).

## Why

End users want durable results and fast cached behavior on whichever cloud
they run on. This package is the plumbing underneath product features such as
"save a job artifact," "list my outputs," and "cache an AI response." Keeping
it behind one interface means we can support AWS, GCP, or Azure — or switch
between them per enterprise customer — without changing product code.

## Scope

| Capability | Interface | Status |
|---|---|---|
| Object storage (S3 / GCS / Blob) | `put` / `get` / `delete` / `list` | implemented |
| Key-value / cache (DynamoDB / Firestore / Cosmos) | same 4 methods + optional TTL | planned (phase 2) |
| Block storage (EBS-like) | separate API | optional, not started |

## Package layout

```
Backend/storage_interface/
├── __init__.py          # public exports
├── base.py              # StorageProvider ABC + ObjectInfo dataclass
├── base_async.py        # AsyncStorageProvider ABC (unified native async I/O)
├── exceptions.py        # StorageError, ObjectNotFoundError, ProviderConfigError
├── config.py            # env loading
├── factory.py           # get_provider("local"|"s3"|"gcs"|"azure")
├── factory_async.py     # get_async_provider (s3|gcs|azure) for unified routes
├── unified.py           # configured cloud ids for unified HTTP (always-on multi-cloud)
├── app.py               # FastAPI wrapper (Postman / curl testable)
├── providers/
│   ├── local.py         # LocalStorageProvider
│   ├── aws_s3.py        # S3StorageProvider (sync)
│   ├── s3_aio.py        # S3AsyncStorageProvider (aioboto3)
│   ├── gcp_gcs.py       # GCSStorageProvider (sync)
│   ├── gcs_aio.py       # GCSAsyncStorageProvider (gcloud-aio-storage)
│   ├── azure_blob.py    # AzureBlobStorageProvider (sync)
│   └── azure_aio.py     # AzureAsyncBlobStorageProvider (azure.storage.blob.aio)
├── requirements.txt
└── .env.example
```

## The interface

```python
class StorageProvider(ABC):
    def put(self, key: str, value: bytes, content_type: str | None = None) -> None: ...
    def get(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...
    def list(self, prefix: str = "") -> list[ObjectInfo]: ...
    def exists(self, key: str) -> bool: ...  # default impl provided
```

Errors: missing keys raise `ObjectNotFoundError`; misconfiguration raises
`ProviderConfigError`. Both subclass `StorageError`.

## Programmatic usage

```python
from Backend.storage_interface import get_provider

store = get_provider("local")           # or "s3" / "gcs" / "azure"
store.put("runs/42/out.log", b"hello")
print(store.get("runs/42/out.log"))
print([o.key for o in store.list("runs/")])
store.delete("runs/42/out.log")
```

## Configuration

Copy `.env.example` to **`.env` inside `Backend/storage_interface/`** and fill
in credentials for the provider(s) you want to test. **This app only loads that
file** — it does not read the Momento repo root `.env` or `Backend/.env`.

For **`get_provider()` in Python**, only that provider's variables are required. For the
**HTTP** `/objects/...` API, set env for **each cloud** you want in the unified set (below); the
server never touches local disk over HTTP.

| Provider | Required env vars |
|---|---|
| `local` | `STORAGE_LOCAL_ROOT` (optional; defaults to `.data/`) — **Python `get_provider("local")` only** |
| `s3` | `AWS_S3_BUCKET`, `AWS_REGION` (+ AWS credentials via env / shared file / IAM) |
| `gcs` | `GCP_GCS_BUCKET`, `GCP_PROJECT`, `GOOGLE_APPLICATION_CREDENTIALS` (or ADC) |
| `azure` | `AZURE_BLOB_CONTAINER`, `AZURE_STORAGE_CONNECTION_STRING` |
| *Unified HTTP* | Same as the three cloud rows: each configured cloud is included automatically. |

## Unified multi-backend HTTP API

`PUT` / `GET` / `DELETE` / `HEAD` on **`/objects/{key}`** always target **every** configured cloud
(S3, GCS, Azure) in parallel. There is **no** `?provider=` query on these routes — that avoids
accidentally writing or reading a single backend while others drift.

**`GET /objects?unified_status=1`** (omit `prefix`) returns which provider ids are in the unified
set and why others are skipped.

**`GET /objects?prefix=...`** lists objects from **all** configured clouds in parallel and returns a
**merged** key list (first-seen metadata wins per key). A **502** is returned if any backend's list
call fails.

| Method | URL | Purpose |
|--------|-----|--------|
| `GET` | `/objects?unified_status=1` | Which cloud ids are in the unified set and skip reasons |
| `GET` | `/objects?prefix=` | Unified async list (merged keys across clouds) |
| `PUT` | `/objects/{key}` | Same body to **every** included cloud; **200 only if all succeed**; rollback on partial failure |
| `GET` | `/objects/{key}` | Read from **every** cloud; **200** only if bytes exist **everywhere** and **match** |
| `DELETE` | `/objects/{key}` | Delete on **every** included cloud (missing key counts as success per store) |
| `HEAD` | `/objects/{key}` | **200** only if the key exists on **every** included cloud |

**Concurrency & async I/O:** calls use `asyncio.gather` with **native async** clients (`aioboto3`,
`gcloud-aio-storage`, `azure.storage.blob.aio`) — no `asyncio.to_thread` on these paths. Wall time
is near the **slowest** cloud. JSON responses include `unified: true`, `parallel: true`, and
`async_io: true` where applicable. Successful **`GET` / `HEAD`** on a key add response header
**`X-Unified-Async-IO: true`** (body is raw bytes on `GET`).

On process shutdown, the app **closes** shared async clients (GCS aiohttp session, Azure transport)
via FastAPI **lifespan**.

**Server console:** unified `PUT` / `GET` / `DELETE` / `HEAD` log `[unified] ... e2e_ms=...`
via **`print` (flushed)** and **`logging.getLogger("momento.storage_interface").info`**.

If **no** cloud backends are configured, object routes return **503** with a short explanation.

## Adding credentials

All secrets live in **`Backend/storage_interface/.env`** only. Copy
`.env.example` to `.env` in that folder, edit values, then **restart uvicorn**
so changes apply. Do not commit `.env` (keep it gitignored).

The **HTTP API** (`app.py`) does not authenticate callers by default; it is
meant for local/dev. Credentials below are for **your server process** talking
to AWS / GCP / Azure — not for Postman headers.

### Local (`STORAGE_PROVIDER=local`)

No cloud credentials. Optional:

| Variable | Purpose |
|----------|---------|
| `STORAGE_LOCAL_ROOT` | Directory where objects are stored as files. Default: `Backend/storage_interface/.data` |

### AWS S3 (`STORAGE_PROVIDER=s3` or `get_provider("s3")`)

**1. Create a bucket** (S3 console) and note **region** (e.g. `us-east-2`).

**2. Create an IAM user** (or reuse one) used only for this dev bucket.

**3. Attach a policy** that allows object + list access to **that bucket only**
(replace `YOUR_BUCKET`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET/*"
    }
  ]
}
```

**4. Create an access key** for that user: IAM → user → **Security credentials**
→ **Create access key** (application running outside AWS). Save the secret once.

**5. Set in `.env`:**

| Variable | Example / notes |
|----------|-----------------|
| `AWS_S3_BUCKET` | Bucket name only, e.g. `my-test-bucket` |
| `AWS_REGION` | Must match the bucket region, e.g. `us-east-2` |
| `AWS_ACCESS_KEY_ID` | From the access key |
| `AWS_SECRET_ACCESS_KEY` | From the access key |

**Alternative:** leave `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` empty
and run `aws configure` once on the machine; boto3 reads
`%USERPROFILE%\.aws\credentials`. You still **must** set `AWS_S3_BUCKET` and
`AWS_REGION` in `.env`.

**Verify outside the app:**

```bash
aws s3 ls s3://YOUR_BUCKET/
```

### GCP Cloud Storage (`STORAGE_PROVIDER=gcs` or `get_provider("gcs")`)

Uses **Application Default Credentials**. Pick **one** auth method.

#### Option A — Service account JSON (typical for laptops)

1. Console → **IAM & Admin → Service accounts** → **Create service account**.
2. **Keys** → **Add key** → **JSON** → download the file (keep it outside the
   repo, e.g. `C:\secrets\gcs-dev.json`).
3. **Cloud Storage → Buckets** → create a bucket in the **same project**.
4. Open the bucket → **Permissions** → **Grant access** → principal = service
   account **email** (`…@PROJECT_ID.iam.gserviceaccount.com`) → role **Storage
   Object Admin** (`roles/storage.objectAdmin`).

**Set in `.env`:**

| Variable | Notes |
|----------|--------|
| `GCP_GCS_BUCKET` | Bucket name only (globally unique), not `gs://` |
| `GCP_PROJECT` | Google Cloud **project ID** (short id, not display name) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Absolute path to the JSON file. On Windows in `.env`, prefer forward slashes: `C:/secrets/gcs-dev.json` |

#### Option B — User Application Default Credentials

Install [Google Cloud SDK](https://cloud.google.com/sdk), then:

```bash
gcloud auth application-default login
```

Set `GCP_GCS_BUCKET` and `GCP_PROJECT`. Leave `GOOGLE_APPLICATION_CREDENTIALS`
empty if ADC is enough.

**Verify outside the app:**

```bash
gcloud storage ls gs://YOUR_BUCKET/
```

### Azure Blob Storage (`STORAGE_PROVIDER=azure` or `get_provider("azure")`)

1. Portal → **Storage accounts** → create or open an account.
2. **Security + networking → Access keys** — copy **Connection string** (key1
   or key2).
3. **Data storage → Containers** → **+ Container** — choose a name (e.g.
   `momento-dev`). Private access is fine.

**Set in `.env`:**

| Variable | Notes |
|----------|--------|
| `AZURE_BLOB_CONTAINER` | Container name you created |
| `AZURE_STORAGE_CONNECTION_STRING` | Full connection string from Access keys |

**Verify outside the app:** use [Azure Storage Explorer](https://azure.microsoft.com/products/storage/storage-explorer/) or the Azure CLI `az storage blob list`.

### Quick troubleshooting

| Symptom | Likely fix |
|---------|------------|
| `AWS_S3_BUCKET is required` / `GCP_GCS_BUCKET is required` | Variable name typo; file must be `storage_interface/.env`; restart server. |
| S3 `PermanentRedirect` / wrong region | `AWS_REGION` must match the bucket’s region. |
| GCS `403` / permission denied | Bucket **Permissions** must include the service account with **Storage Object Admin** on that bucket. |
| `DefaultCredentialsError` (GCP) | Set `GOOGLE_APPLICATION_CREDENTIALS` or run `gcloud auth application-default login`. |
| Azure `403` / container not found | Check container name spelling; connection string must be for the same storage account. |

## Install and run

```bash
# From the repo root
pip install -r Backend/storage_interface/requirements.txt

# Run the HTTP wrapper so Postman / curl can exercise the interface
uvicorn Backend.storage_interface.app:app --reload --port 8100
```

Once running:

- OpenAPI / Swagger UI: <http://localhost:8100/docs>
- ReDoc: <http://localhost:8100/redoc>

## Testing

### 1. Prerequisites

The HTTP API is **unified-only**: configure **at least one** of S3 / GCS / Azure in
`Backend/storage_interface/.env`. Local filesystem tests use **`get_provider("local")`**
in Python, not these HTTP routes.

### 2. Postman

Base URL `http://localhost:8100` (adjust if needed):

| # | Method | URL | Body | Notes |
|---|---|---|---|---|
| 1 | GET | `/health` | — | expect `{"status":"ok"}` |
| 2 | GET | `/providers` | — | `unified_includes` + `skips` |
| 3 | GET | `/objects?unified_status=1` | — | which clouds are active |
| 4 | PUT | `/objects/smoke/hello.txt` | **Body → raw → Text**: `hello world` | unified PUT JSON response |
| 5 | PUT | `/objects/smoke/meta.json` | **Body → raw → JSON**: `{"value_text": "{}", "content_type": "application/json"}` | JSON body mode |
| 6 | GET | `/objects?prefix=smoke/` | — | merged unified list JSON |
| 7 | GET | `/objects/smoke/hello.txt` | — | raw bytes; check header `X-Unified-Async-IO: true` |
| 8 | HEAD | `/objects/smoke/hello.txt` | — | 200 only if key exists on every cloud |
| 9 | DELETE | `/objects/smoke/hello.txt` | — | unified delete JSON |

### 3. curl quick check

```bash
curl "http://localhost:8100/objects?unified_status=1"

# Writes to every configured cloud (requires AWS/GCP/Azure env in .env)
curl -X PUT "http://localhost:8100/objects/smoke/unified.txt" --data "hello-all" -H "Content-Type: text/plain"
curl -i "http://localhost:8100/objects/smoke/unified.txt"
curl "http://localhost:8100/objects?prefix=smoke/"
curl -I "http://localhost:8100/objects/smoke/unified.txt"
curl -X DELETE "http://localhost:8100/objects/smoke/unified.txt"
```

### 4. Acceptance checklist

With **all** intended clouds configured, confirm:

1. `PUT /objects/smoke/a.txt` → `200` and JSON `{"ok": true, "unified": true, "async_io": true, ...}`
2. `GET /objects/smoke/a.txt` → `200` with the exact bytes; response includes `X-Unified-Async-IO: true`
3. `GET /objects?prefix=smoke/` → JSON with `unified`, `async_io`, and merged `objects`
4. `DELETE /objects/smoke/a.txt` → `200` and per-provider results
5. `GET /objects/smoke/a.txt` → `404` (or `409` if drift) with JSON `detail` including `async_io`

### 5. Pre-flight credential checks (outside this service)

Before pointing the API at AWS/GCP, confirm the credentials themselves work:

```bash
# AWS
aws s3 ls s3://$AWS_S3_BUCKET/

# GCP (requires gcloud and gsutil / gcloud storage)
gcloud storage ls gs://$GCP_GCS_BUCKET/
```

If either command fails, the storage interface will fail the same way — fix
the credentials first.

## Roadmap

- [ ] Add `ttl` kwarg to `put` for the KV/cache backends (DynamoDB / Firestore / Cosmos).
- [ ] Streaming `put_stream` / `get_stream` for large artifacts.
- [ ] Server-side copy (`copy(src, dst)`) to avoid round-tripping bytes through the client.
- [ ] Pluggable content addressing (hash-prefixed keys) for dedup.
