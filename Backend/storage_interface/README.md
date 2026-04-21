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
├── exceptions.py        # StorageError, ObjectNotFoundError, ProviderConfigError
├── config.py            # env loading
├── factory.py           # get_provider("local"|"s3"|"gcs"|"azure")
├── app.py               # FastAPI wrapper (Postman / curl testable)
├── providers/
│   ├── local.py         # LocalStorageProvider
│   ├── aws_s3.py        # S3StorageProvider
│   ├── gcp_gcs.py       # GCSStorageProvider
│   └── azure_blob.py    # AzureBlobStorageProvider
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

Only the active provider's variables are required.

| Provider | Required env vars |
|---|---|
| `local` | `STORAGE_LOCAL_ROOT` (optional; defaults to `.data/`) |
| `s3` | `AWS_S3_BUCKET`, `AWS_REGION` (+ AWS credentials via env / shared file / IAM) |
| `gcs` | `GCP_GCS_BUCKET`, `GCP_PROJECT`, `GOOGLE_APPLICATION_CREDENTIALS` (or ADC) |
| `azure` | `AZURE_BLOB_CONTAINER`, `AZURE_STORAGE_CONNECTION_STRING` |

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

### AWS S3 (`STORAGE_PROVIDER=s3` or `?provider=s3`)

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

### GCP Cloud Storage (`STORAGE_PROVIDER=gcs` or `?provider=gcs`)

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

### Azure Blob Storage (`STORAGE_PROVIDER=azure` or `?provider=azure`)

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

### 1. Pick a provider

Every HTTP request supports a `?provider=` query parameter, which overrides
`STORAGE_PROVIDER` from the `.env` file. Valid values: `local`, `s3`, `gcs`,
`azure`.

Examples:

- `?provider=local` — filesystem, no credentials needed (sanity check)
- `?provider=s3` — talks to AWS using your configured credentials and bucket
- `?provider=gcs` — talks to GCP using ADC / service-account JSON

### 2. Postman

A minimal workflow (each request targets `http://localhost:8100`):

| # | Method | URL | Body | Notes |
|---|---|---|---|---|
| 1 | GET | `/health` | — | expect `{"status":"ok"}` |
| 2 | GET | `/providers` | — | lists compiled-in providers |
| 3 | PUT | `/objects/hello.txt?provider=local` | **Body → raw → Text**: `hello world` | stores plain text; server uses body as-is |
| 4 | PUT | `/objects/runs/42/meta.json?provider=local` | **Body → raw → JSON**:<br>`{"value_text": "{\"ok\": true}", "content_type": "application/json"}` | JSON mode with `value_text` |
| 5 | PUT | `/objects/logo.bin?provider=local` | **Body → raw → JSON**:<br>`{"value_base64": "aGVsbG8=", "content_type": "application/octet-stream"}` | JSON mode with base64 bytes |
| 6 | GET | `/objects` | query: `prefix=runs/` | lists everything under `runs/` |
| 7 | GET | `/objects/hello.txt?provider=local` | — | downloads the bytes (Postman shows raw text) |
| 8 | HEAD | `/objects/hello.txt?provider=local` | — | 200 if present, 404 otherwise |
| 9 | DELETE | `/objects/hello.txt?provider=local` | — | removes the key |

Once the local flow works, change `?provider=` to `s3` or `gcs` and repeat to
validate real cloud credentials.

Tip: create a Postman **environment** with a `baseUrl` variable
(`http://localhost:8100`) and a `provider` variable so each request can use
`{{baseUrl}}/objects/{{key}}?provider={{provider}}`.

### 3. curl quick check

```bash
# Local
curl -X PUT  "http://localhost:8100/objects/hello.txt?provider=local"      --data "hello world" -H "Content-Type: text/plain"
curl       "http://localhost:8100/objects/hello.txt?provider=local"
curl       "http://localhost:8100/objects?prefix=&provider=local"
curl -X DELETE "http://localhost:8100/objects/hello.txt?provider=local"

# AWS S3 (after filling AWS_S3_BUCKET / credentials in .env)
curl -X PUT  "http://localhost:8100/objects/smoke/test.txt?provider=s3"      --data "from-s3" -H "Content-Type: text/plain"
curl       "http://localhost:8100/objects/smoke/test.txt?provider=s3"

# GCP GCS
curl -X PUT  "http://localhost:8100/objects/smoke/test.txt?provider=gcs"      --data "from-gcs" -H "Content-Type: text/plain"
curl       "http://localhost:8100/objects/smoke/test.txt?provider=gcs"
```

### 4. Acceptance checklist

Before calling a provider "done," run this sequence against it and confirm all
five pass:

1. `PUT /objects/smoke/a.txt` → `200 {"ok": true, ...}`
2. `GET /objects/smoke/a.txt` → `200` with the exact bytes sent
3. `GET /objects?prefix=smoke/` → `count >= 1`, includes `smoke/a.txt`
4. `DELETE /objects/smoke/a.txt` → `200`
5. `GET /objects/smoke/a.txt` → `404 not found: smoke/a.txt`

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
