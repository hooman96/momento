"""Configuration loader for the storage interface.

Reads environment variables (optionally from a `.env` file in this package)
so provider classes stay free of `os.environ` access.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Storage API only reads this package's `.env` (not repo root or `Backend/.env`).
_pkg_dir = Path(__file__).resolve().parent
load_dotenv(_pkg_dir / ".env")


def _get(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


# Which provider the factory should return by default.
DEFAULT_PROVIDER = _get("STORAGE_PROVIDER", "local").lower()

# Local filesystem backend (dev/testing).
LOCAL_ROOT = _get("STORAGE_LOCAL_ROOT", str(Path(__file__).resolve().parent / ".data"))

# AWS S3
AWS_BUCKET = _get("AWS_S3_BUCKET")
AWS_REGION = _get("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = _get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = _get("AWS_SECRET_ACCESS_KEY")

# GCP GCS
GCP_BUCKET = _get("GCP_GCS_BUCKET")
GCP_PROJECT = _get("GCP_PROJECT")
# Path to a service account JSON. If unset, Application Default Credentials
# (e.g. `gcloud auth application-default login`) are used.
GCP_CREDENTIALS_FILE = _get("GOOGLE_APPLICATION_CREDENTIALS")

# Azure Blob
AZURE_CONTAINER = _get("AZURE_BLOB_CONTAINER")
AZURE_CONNECTION_STRING = _get("AZURE_STORAGE_CONNECTION_STRING")

