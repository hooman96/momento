#!/usr/bin/env python3
"""
GitHub Cloud Infrastructure Scraper
=====================================
Production-grade scraper that extracts cloud infrastructure metadata and logs
from public GitHub repositories, normalising results into a structured CSV.

Targets AWS, Azure, and GCP artifacts — Terraform, Kubernetes, CloudFormation,
CI/CD pipelines, and deployment/application logs.

Usage:
    export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    # Run with defaults
    python github_cloudInfra_scraper.py

    # Custom run
    python github_cloudInfra_scraper.py \\
        --keywords "aws terraform" "gcp kubernetes" \\
        --max-repos 50 --workers 8 \\
        --output cloud_infra_github_dataset.csv

    # Use GraphQL API + verbose logging
    python github_cloudInfra_scraper.py --use-graphql --verbose

Requirements:
    pip install requests pandas
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import logging
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Generator, Optional

import requests

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("cloud_infra_scraper")

# Constants
GITHUB_API = "https://api.github.com"
GITHUB_GRAPHQL = "https://api.github.com/graphql"
MAX_FILE_SIZE = 1_000_000  # 1 MB — skip anything larger

DEFAULT_KEYWORDS: list[str] = [
    "aws terraform infrastructure",
    "azure kubernetes deployment",
    "gcp cloudformation devops",
    "github actions ci/cd pipeline",
    "infrastructure as code terraform",
    "kubernetes helm deployment",
]

TARGET_EXTENSIONS: frozenset[str] = frozenset(
    {".tf", ".tfvars", ".yaml", ".yml", ".json", ".log", ".sh", ".template"}
)
TARGET_PATH_SEGMENTS: frozenset[str] = frozenset(
    {
        ".github/workflows",
        "k8s",
        "kubernetes",
        "terraform",
        "infra",
        "deploy",
        "ci",
        ".circleci",
        "cloudformation",
        "ansible",
        "helm",
        "charts",
        "logs",
    }
)

CSV_FIELDS: list[str] = [
    "repo_full_name",
    "repo_url",
    "repo_star",
    "repo_language",
    "repo_created_at",
    "repo_updated_at",
    "cloud_provider",
    "resource_types",
    "region",
    "environment",
    "tags",
    "log_type",
    "log_snippet",
]


# Cloud-provider detection — regex patterns
_AWS_PATTERNS: list[str] = [
    r"\bAWS::",
    r"\baws_",
    r"amazonaws\.com",
    r"arn:aws:",
    r"s3://",
    r'provider\s*=\s*"aws"',
    r'source\s*=\s*"hashicorp/aws"',
    r"\bboto3\b",
    r"\bbotocore\b",
    r"amazon-linux",
    r"\bec2\b",
    r"\beks\b",
    r"\becs\b",
]

_AZURE_PATTERNS: list[str] = [
    r"\bazurerm_",
    r"\bMicrosoft\.\w+",
    r"azure\.com",
    r"\.azure\.",
    r'provider\s*=\s*"azurerm"',
    r'source\s*=\s*"hashicorp/azurerm"',
    r"\baks\b",
    r"azurewebsites\.net",
    r"@azure/",
    r"azure-mgmt-",
]

_GCP_PATTERNS: list[str] = [
    r"\bgoogle_",
    r"\bgcp_",
    r"googleapis\.com",
    r"\bgcloud\b",
    r'provider\s*=\s*"google"',
    r'source\s*=\s*"hashicorp/google"',
    r"\bgke\b",
    r"\bbigquery\b",
    r"gcr\.io",
    r"gs://",
    r"google-cloud-",
    r"from google\.cloud",
]

_RE_AWS_PROVIDER = re.compile("|".join(_AWS_PATTERNS), re.IGNORECASE)
_RE_AZURE_PROVIDER = re.compile("|".join(_AZURE_PATTERNS), re.IGNORECASE)
_RE_GCP_PROVIDER = re.compile("|".join(_GCP_PATTERNS), re.IGNORECASE)

_RE_AWS_REGION = re.compile(
    r"\b(us-east-[12]|us-west-[12]|eu-west-[123]|eu-central-1"
    r"|ap-southeast-[123]|ap-northeast-[123]|sa-east-1"
    r"|ca-central-1|ap-south-1|me-south-1|af-south-1)\b"
)
_RE_AZURE_REGION = re.compile(
    r"\b(eastus2?|westus[23]?|northeurope|westeurope|uksouth|ukwest"
    r"|australiaeast|southeastasia|eastasia|japaneast|japanwest"
    r"|canadacentral|brazilsouth|centralindia|southindia)\b",
    re.IGNORECASE,
)
_RE_GCP_REGION = re.compile(
    r"\b(us-central1|us-east[14]|us-west[1-4]|europe-west[1-6]|europe-north1"
    r"|asia-east[12]|asia-northeast[123]|asia-southeast[12]"
    r"|australia-southeast1|southamerica-east1|northamerica-northeast[12])\b"
)

_RE_AWS_RESOURCES = re.compile(
    r"AWS::([\w]+)::([\w]+)"
    r"|resource\s+\"(aws_[\w]+)\""
    r"|\b(ec2|s3|rds|lambda|ecs|eks|elb|alb|nlb|cloudfront|route53"
    r"|dynamodb|sqs|sns|iam|kms|vpc|subnet|security.?group|cloudwatch)\b",
    re.IGNORECASE,
)
_RE_AZURE_RESOURCES = re.compile(
    r"(azurerm_[\w]+)"
    r"|Microsoft\.([\w]+)/([\w]+)"
    r"|\b(vm|aks|acr|appservice|functions|cosmosdb|servicebus"
    r"|eventhub|keyvault|storage.account|virtual.?network|nsg)\b",
    re.IGNORECASE,
)
_RE_GCP_RESOURCES = re.compile(
    r"(google_[\w]+)"
    r"|\b(gke|gcs|bigquery|pubsub|cloud.?run|cloud.?functions"
    r"|compute.?engine|cloud.?sql|gce|artifact.?registry)\b",
    re.IGNORECASE,
)
_RE_K8S_KIND = re.compile(r"^kind:\s*(\w+)", re.MULTILINE)

_RE_ENVIRONMENT = re.compile(
    r"\b(prod(?:uction)?|staging|stage|dev(?:elopment)?|qa"
    r"|test(?:ing)?|sandbox|uat|preview|preprod|pre-prod)\b",
    re.IGNORECASE,
)

_RE_TAGS_HCL = re.compile(
    r'(?:tags|labels)\s*=\s*\{([^}]{1,500})\}', re.IGNORECASE | re.DOTALL
)
_RE_TAGS_YAML = re.compile(
    r'(?:tags|labels)\s*:\s*\n((?:[ \t]+[\w\-]+\s*:\s*\S+\n?){1,15})',
    re.IGNORECASE,
)
_RE_KV = re.compile(r'([\w\-]+)\s*[=:]\s*["\']?([^\s"\'}\n,]{1,60})["\']?')

_LOG_PATTERNS: dict[str, re.Pattern[str]] = {
    "access": re.compile(
        r"(GET|POST|PUT|DELETE|PATCH)\s+/\S+\s+HTTP/\d", re.IGNORECASE
    ),
    "error": re.compile(
        r"\b(ERROR|EXCEPTION|FATAL|CRITICAL|FAILED|FAILURE)\b", re.IGNORECASE
    ),
    "audit": re.compile(
        r"\b(AUDIT|audit_log|access_log|security_log)\b", re.IGNORECASE
    ),
    "deployment": re.compile(
        r"\b(deploy(?:ment)?|release|rollout|helm install|kubectl apply"
        r"|docker push|pushed to)\b",
        re.IGNORECASE,
    ),
}

# Secret masking — two-group patterns keep the key name, redact the value
_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"((?:password|passwd|pwd|secret|api_?key|auth_?token|access_?token"
            r"|private_?key|aws_?secret|client_?secret)\s*[=:]\s*[\"']?)([^\s\"']{8,})",
            re.IGNORECASE,
        ),
        r"\1[REDACTED]",
    ),
    (
        re.compile(r"((ghp|gho|ghu|ghs|ghr)_)[A-Za-z0-9]{36}"),
        r"\1[REDACTED]",
    ),
    (
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "[REDACTED-AWS-KEY]",
    ),
    (
        re.compile(r"\b[0-9a-f]{40}\b"),  # Git SHA / bearer tokens
        "[REDACTED-TOKEN]",
    ),
]


# Data schema
@dataclass
class CloudInfraRecord:
    """One row in the output CSV."""

    repo_full_name: str = ""
    repo_url: str = ""
    repo_star: int = 0
    repo_language: str = ""
    repo_created_at: str = ""
    repo_updated_at: str = ""
    cloud_provider: str = ""
    resource_types: str = ""
    region: str = ""
    environment: str = ""
    tags: str = ""
    log_type: str = ""
    log_snippet: str = ""

    def content_hash(self) -> str:
        """Stable hash for deduplication across records."""
        key = (
            f"{self.repo_full_name}|{self.cloud_provider}"
            f"|{self.resource_types}|{self.log_snippet[:80]}"
        )
        return hashlib.md5(key.encode()).hexdigest()

# File cache
class FileCache:
    """
    Lightweight JSON file cache that avoids re-fetching unchanged content
    across script runs.  Thread-safe via per-key locking.
    """

    def __init__(self, cache_dir: str = ".scraper_cache") -> None:
        self._dir = Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self, key: str) -> Path:
        h = hashlib.sha256(key.encode()).hexdigest()
        return self._dir / f"{h}.json"

    def get(self, key: str) -> Any:
        """Return cached value or None if absent/corrupt."""
        p = self._path(key)
        try:
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
        return None

    def set(self, key: str, value: Any) -> None:
        """Persist *value* under *key*; silently ignores write failures."""
        p = self._path(key)
        try:
            with self._lock:
                p.write_text(json.dumps(value, default=str), encoding="utf-8")
        except Exception:
            pass


# GitHub API client
class GitHubClient:
    """
    Thread-safe GitHub REST (and optional GraphQL) API client.

    Features:
    - Automatic rate-limit detection and sleep-until-reset
    - Exponential backoff on transient errors (429, 5xx, connection drops)
    - Transparent pagination via Link headers
    - Optional response caching via FileCache
    """

    def __init__(
        self,
        token: Optional[str] = None,
        cache: Optional[FileCache] = None,
    ) -> None:
        self._cache = cache
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "cloud-infra-scraper/2.0",
            }
        )
        if token:
            self._session.headers["Authorization"] = f"Bearer {token}"
            log.info("GitHub token loaded — 5,000 req/h core, 30 req/min search")
        else:
            log.warning("No GITHUB_TOKEN — limited to 60 req/h (10 search/min)")

    # Internal helpers
    def _handle_rate_limit(self, resp: requests.Response) -> None:
        """Block until the rate-limit window resets when quota is exhausted."""
        remaining = int(resp.headers.get("X-RateLimit-Remaining", 1))
        if remaining > 0:
            return
        reset_ts = int(resp.headers.get("X-RateLimit-Reset", 0))
        sleep_s = max(reset_ts - int(time.time()), 1) + 2
        log.warning("Rate limit exhausted — sleeping %d s", sleep_s)
        time.sleep(sleep_s)

    def _get(
        self,
        url: str,
        params: Optional[dict[str, Any]] = None,
        max_retries: int = 5,
    ) -> requests.Response:
        """
        GET *url* with exponential backoff on transient failures.

        Raises:
            requests.HTTPError: on unrecoverable HTTP errors.
        """
        backoff = 2
        for attempt in range(max_retries):
            try:
                resp = self._session.get(url, params=params, timeout=30)
            except (requests.ConnectionError, requests.Timeout) as exc:
                log.warning("Connection error attempt %d/%d: %s", attempt + 1, max_retries, exc)
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue

            if resp.status_code == 200:
                self._handle_rate_limit(resp)
                return resp

            if resp.status_code in (403, 429):
                self._handle_rate_limit(resp)
                continue  # retry after sleeping

            if resp.status_code == 404:
                resp.raise_for_status()

            if resp.status_code == 422:
                log.error("Validation error for %s: %s", url, resp.text[:300])
                resp.raise_for_status()

            if resp.status_code >= 500:
                log.warning(
                    "HTTP %d on %s — retry %d/%d",
                    resp.status_code, url, attempt + 1, max_retries,
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue

            resp.raise_for_status()

        raise requests.HTTPError(f"Max retries exceeded for GET {url}")

    def _paginate(
        self,
        url: str,
        params: dict[str, Any],
        max_pages: int = 10,
    ) -> Generator[dict[str, Any], None, None]:
        """Yield JSON page bodies, following GitHub Link headers."""
        for page in range(1, max_pages + 1):
            resp = self._get(url, {**params, "page": page})
            yield resp.json()
            if 'rel="next"' not in resp.headers.get("Link", ""):
                break

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search_repos(
        self,
        query: str,
        max_repos: int = 30,
        min_stars: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Search public repositories via the REST Search API.

        Args:
            query:     GitHub search query string.
            max_repos: Maximum number of repositories to return.
            min_stars: Minimum star count filter.

        Returns:
            List of repository objects (GitHub API shape).
        """
        full_query = f"{query} stars:>{min_stars}"
        per_page = min(max_repos, 100)
        max_pages = (max_repos + per_page - 1) // per_page
        repos: list[dict[str, Any]] = []

        for page_body in self._paginate(
            f"{GITHUB_API}/search/repositories",
            {"q": full_query, "sort": "stars", "order": "desc", "per_page": per_page},
            max_pages=max_pages,
        ):
            repos.extend(page_body.get("items", []))
            if len(repos) >= max_repos:
                break
            time.sleep(2)  # respect the search API's stricter throttle

        return repos[:max_repos]

    def search_repos_graphql(
        self,
        query: str,
        max_repos: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Search repositories via the GitHub GraphQL API (bonus feature).

        Returns normalised dicts compatible with :meth:`search_repos` output.
        """
        gql = """
        query($q: String!, $cursor: String) {
          search(query: $q, type: REPOSITORY, first: 20, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              ... on Repository {
                nameWithOwner
                url
                stargazerCount
                primaryLanguage { name }
                createdAt
                updatedAt
                defaultBranchRef { name }
              }
            }
          }
        }
        """
        repos: list[dict[str, Any]] = []
        cursor: Optional[str] = None

        while len(repos) < max_repos:
            try:
                resp = self._session.post(
                    GITHUB_GRAPHQL,
                    json={"query": gql, "variables": {"q": query, "cursor": cursor}},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                log.warning("GraphQL request failed: %s", exc)
                break

            search_data = data.get("data", {}).get("search", {})
            for node in search_data.get("nodes", []):
                if not node:
                    continue
                repos.append(
                    {
                        "full_name": node["nameWithOwner"],
                        "html_url": node.get("url", ""),
                        "stargazers_count": node.get("stargazerCount", 0),
                        "language": (node.get("primaryLanguage") or {}).get("name", ""),
                        "created_at": node.get("createdAt", ""),
                        "updated_at": node.get("updatedAt", ""),
                        "default_branch": (node.get("defaultBranchRef") or {}).get("name", "main"),
                    }
                )

            page_info = search_data.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")

        return repos[:max_repos]

    def get_tree(self, owner: str, repo: str, branch: str = "HEAD") -> list[dict[str, Any]]:
        """
        Return the full recursive file tree for *branch*.

        Args:
            owner:  Repository owner login.
            repo:   Repository name.
            branch: Branch or commit SHA (default: HEAD).
        """
        url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}"
        resp = self._get(url, {"recursive": "1"})
        body = resp.json()
        if body.get("truncated"):
            log.warning("Tree truncated for %s/%s — large repo", owner, repo)
        return body.get("tree", [])

    def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
    ) -> Optional[str]:
        """
        Fetch and decode the UTF-8 text content of a single file.

        Returns None on any failure (404, binary, decode error, etc.).
        Results are cached to avoid redundant API calls on re-runs.
        """
        cache_key = f"file:{owner}/{repo}/{path}"
        if self._cache:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
        try:
            resp = self._get(url)
        except requests.HTTPError:
            return None

        data = resp.json()
        if data.get("encoding") != "base64" or not data.get("content"):
            return None

        try:
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None

        if self._cache:
            self._cache.set(cache_key, content)
        return content


# ---------------------------------------------------------------------------
# Cloud-analysis helpers
# ---------------------------------------------------------------------------


def mask_secrets(text: str) -> str:
    """
    Replace credential-like strings with [REDACTED] placeholders.

    Preserves key names so context is retained; only values are masked.
    """
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def detect_cloud_providers(text: str, file_path: str = "") -> list[str]:
    """
    Identify which cloud providers (AWS, Azure, GCP) are referenced.

    Checks both file content and file path for provider-specific patterns.

    Args:
        text:      Decoded file content.
        file_path: Relative path of the file within the repository.

    Returns:
        Sorted list of detected provider names (e.g. ["AWS", "GCP"]).
    """
    combined = text + " " + file_path
    providers: list[str] = []
    if _RE_AWS_PROVIDER.search(combined):
        providers.append("AWS")
    if _RE_AZURE_PROVIDER.search(combined):
        providers.append("Azure")
    if _RE_GCP_PROVIDER.search(combined):
        providers.append("GCP")
    return providers


def extract_resource_types(text: str, providers: list[str]) -> list[str]:
    """
    Extract cloud resource type identifiers (e.g. aws_s3_bucket, Deployment).

    Args:
        text:      File content.
        providers: List of detected providers from :func:`detect_cloud_providers`.

    Returns:
        Deduplicated, sorted list of resource type strings (capped at 20).
    """
    resources: set[str] = set()

    if "AWS" in providers:
        for m in _RE_AWS_RESOURCES.finditer(text):
            r = next((g.strip() for g in m.groups() if g), None)
            if r:
                resources.add(r)

    if "Azure" in providers:
        for m in _RE_AZURE_RESOURCES.finditer(text):
            r = next((g.strip() for g in m.groups() if g), None)
            if r:
                resources.add(r)

    if "GCP" in providers:
        for m in _RE_GCP_RESOURCES.finditer(text):
            r = next((g.strip() for g in m.groups() if g), None)
            if r:
                resources.add(r)

    resources.update(_RE_K8S_KIND.findall(text))

    return sorted(resources)[:20]


def extract_region(text: str, providers: list[str]) -> str:
    """
    Extract cloud region identifiers from file content.

    Returns:
        Comma-separated, sorted unique region strings.
    """
    regions: set[str] = set()
    if "AWS" in providers:
        regions.update(_RE_AWS_REGION.findall(text))
    if "Azure" in providers:
        regions.update(m.lower() for m in _RE_AZURE_REGION.findall(text))
    if "GCP" in providers:
        regions.update(_RE_GCP_REGION.findall(text))
    return ", ".join(sorted(regions))


def extract_environment(text: str, file_path: str = "") -> str:
    """
    Detect deployment environment labels (prod, staging, dev, qa, …).

    Searches the first 2,000 characters of content and the file path.

    Returns:
        Comma-separated, sorted unique environment strings.
    """
    haystack = text[:2_000] + " " + file_path
    envs: set[str] = set()
    for m in _RE_ENVIRONMENT.finditer(haystack):
        env = m.group(1).lower()
        if env.startswith("prod"):
            env = "production"
        elif env.startswith("dev"):
            env = "development"
        elif env in ("stage", "staging"):
            env = "staging"
        envs.add(env)
    return ", ".join(sorted(envs))


def extract_tags(text: str) -> str:
    """
    Extract tag/label key-value pairs from HCL or YAML content.

    Returns:
        Semicolon-separated list of key=value strings (capped at 20 pairs).
    """
    pairs: list[str] = []
    for pattern in (_RE_TAGS_HCL, _RE_TAGS_YAML):
        for block_match in pattern.finditer(text):
            block = block_match.group(1) or ""
            for k, v in _RE_KV.findall(block)[:10]:
                pairs.append(f"{k}={v}")
    return "; ".join(pairs[:20])


def detect_log_type(text: str, file_path: str = "") -> str:
    """
    Classify log content by type (access, error, audit, deployment).

    Returns:
        Comma-separated list of matched log type labels.
    """
    found: list[str] = [ltype for ltype, pat in _LOG_PATTERNS.items() if pat.search(text)]
    lower_path = file_path.lower()
    for hint in ("access", "error", "audit", "deploy"):
        if hint in lower_path and hint not in found:
            found.append(hint)
    return ", ".join(found)


def extract_log_snippet(text: str, log_type: str) -> str:
    """
    Extract a representative, secret-masked snippet from log content.
    Args:
        text:      File content.
        log_type:  Comma-separated log type labels from :func:`detect_log_type`.
    Returns:
        A tuple of (snippet, total_chars) where snippet is the pipe-separated
        matching lines and total_chars is its length.
    """
    if not log_type:
        return ""

    active_types = [t.strip() for t in log_type.split(",")]
    snippet_lines: list[str] = []
    
    for line in text.splitlines():
        for ltype in active_types:
            pat = _LOG_PATTERNS.get(ltype)
            if pat and pat.search(line):
                snippet_lines.append(line.strip())
                break
    
    snippet = mask_secrets(" | ".join(snippet_lines))
    return snippet


# File-level filtering
def is_target_file(path: str, size: int) -> bool:
    """
    Return True if the file should be fetched and analysed.

    Skips:
    - Files larger than MAX_FILE_SIZE (1 MB).
    - Files whose extension is not in TARGET_EXTENSIONS, unless the
      path resides inside a TARGET_PATH_SEGMENTS directory.
    """
    if size > MAX_FILE_SIZE:
        return False
    ext = PurePosixPath(path).suffix.lower()
    lower = path.lower()
    if ext in TARGET_EXTENSIONS:
        return True
    return any(seg in lower for seg in TARGET_PATH_SEGMENTS)


# Main scraper orchestrator
class CloudInfraScraper:
    """
    Orchestrates: keyword search → tree walk → parallel file fetch →
    cloud analysis → deduplication → CSV output.

    Thread safety:
        :attr:`_seen_hashes` is protected by :attr:`_lock` so that multiple
        worker threads can call :meth:`_process_file` concurrently.
    """

    def __init__(
        self,
        client: GitHubClient,
        keywords: list[str],
        max_repos_per_query: int = 20,
        max_files_per_repo: int = 50,
        min_stars: int = 50,
        workers: int = 4,
        use_graphql: bool = False,
    ) -> None:
        self.client = client
        self.keywords = keywords
        self.max_repos = max_repos_per_query
        self.max_files = max_files_per_repo
        self.min_stars = min_stars
        self.workers = workers
        self.use_graphql = use_graphql

        self._records: list[CloudInfraRecord] = []
        self._seen_hashes: set[str] = set()
        self._lock = threading.Lock()


    # Public interface
    def run(self) -> list[CloudInfraRecord]:
        """
        Execute the full scrape pipeline and return deduplicated records.

        Returns:
            List of :class:`CloudInfraRecord` instances ready for CSV export.
        """
        all_repos = self._collect_repos()
        unique_repos = self._deduplicate_repos(all_repos)
        log.info("Processing %d unique repositories", len(unique_repos))

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(self._process_repo, repo): repo for repo in unique_repos}
            for future in as_completed(futures):
                repo_name = futures[future].get("full_name", "?")
                try:
                    self._records.extend(future.result())
                except Exception as exc:
                    log.error("Error processing %s: %s", repo_name, exc)

        log.info("Scrape complete — %d records collected", len(self._records))
        return self._records

    # Internal pipeline stages
    def _collect_repos(self) -> list[dict[str, Any]]:
        """Run all keyword queries and aggregate raw repository objects."""
        all_repos: list[dict[str, Any]] = []
        for keyword in self.keywords:
            log.info("Querying: %s", keyword)
            try:
                if self.use_graphql:
                    repos = self.client.search_repos_graphql(keyword, max_repos=self.max_repos)
                else:
                    repos = self.client.search_repos(
                        keyword, max_repos=self.max_repos, min_stars=self.min_stars
                    )
                log.info("  → %d repos found", len(repos))
                all_repos.extend(repos)
            except Exception as exc:
                log.error("Search failed for '%s': %s", keyword, exc)
        return all_repos

    @staticmethod
    def _deduplicate_repos(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove duplicate repos by full_name, preserving insertion order."""
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for repo in repos:
            name = repo.get("full_name", "")
            if name and name not in seen:
                seen.add(name)
                unique.append(repo)
        return unique

    def _process_repo(self, repo: dict[str, Any]) -> list[CloudInfraRecord]:
        """
        Fetch the file tree for *repo*, filter interesting files, and
        analyse each one.

        Args:
            repo: GitHub repository object (REST or normalised GraphQL shape).

        Returns:
            List of :class:`CloudInfraRecord` for this repository.
        """
        full_name: str = repo["full_name"]
        owner, name = full_name.split("/", 1)
        branch: str = repo.get("default_branch", "main")

        log.info("Processing %s (★%d)", full_name, repo.get("stargazers_count", 0))

        try:
            tree = self.client.get_tree(owner, name, branch=branch)
        except Exception as exc:
            log.warning("Skipping %s — tree fetch failed: %s", full_name, exc)
            return []

        candidates = sorted(
            (
                entry
                for entry in tree
                if entry.get("type") == "blob"
                and is_target_file(entry["path"], entry.get("size", 0))
            ),
            key=lambda e: e.get("size", 0),  # smallest files first
        )[: self.max_files]

        records: list[CloudInfraRecord] = []
        for entry in candidates:
            records.extend(self._process_file(repo, entry, owner, name))
        return records

    def _process_file(
        self,
        repo: dict[str, Any],
        entry: dict[str, Any],
        owner: str,
        repo_name: str,
    ) -> list[CloudInfraRecord]:
        """
        Fetch and analyse a single file, returning 0 or 1 records.

        Files are skipped if:
        - Content cannot be fetched.
        - No cloud provider is detected and the file is not a log.
        - The computed record hash has already been seen (duplicate).
        """
        path: str = entry["path"]
        content = self.client.get_file_content(owner, repo_name, path)
        if not content:
            return []

        providers = detect_cloud_providers(content, path)
        is_log = path.lower().endswith(".log") or "logs/" in path.lower()

        if not providers and not is_log:
            return []

        resource_types = extract_resource_types(content, providers)
        region = extract_region(content, providers)
        environment = extract_environment(content, path)
        tags = extract_tags(content)
        log_type = detect_log_type(content, path)
        log_snippet = extract_log_snippet(content, log_type)

        rec = CloudInfraRecord(
            repo_full_name=repo["full_name"],
            repo_url=repo.get("html_url", ""),
            repo_star=repo.get("stargazers_count", 0),
            repo_language=repo.get("language") or "",
            repo_created_at=repo.get("created_at", ""),
            repo_updated_at=repo.get("updated_at", ""),
            cloud_provider=", ".join(providers),
            resource_types=", ".join(resource_types),
            region=region,
            environment=environment,
            tags=tags,
            log_type=log_type,
            log_snippet=log_snippet,
        )

        if not rec.log_snippet:
            return []

        h = rec.content_hash()
        with self._lock:
            if h in self._seen_hashes:
                return []
            self._seen_hashes.add(h)

        log.debug("  + %s  [provider=%s]", path, rec.cloud_provider or "log")
        return [rec]


# CSV / DataFrame output
def write_csv(records: list[CloudInfraRecord], output_path: str) -> None:
    """
    Write *records* to a CSV file at *output_path*.

    Performs a final deduplication pass on all CSV fields before writing.
    Uses pandas when available for richer DataFrame operations; falls back
    to the built-in csv module otherwise.

    Args:
        records:     List of scraped records.
        output_path: Destination file path.
    """
    rows: list[dict[str, Any]] = []
    seen_row_hashes: set[str] = set()

    for rec in records:
        row = {f: getattr(rec, f) for f in CSV_FIELDS}
        row_hash = hashlib.md5(json.dumps(row, sort_keys=True).encode()).hexdigest()
        if row_hash not in seen_row_hashes:
            seen_row_hashes.add(row_hash)
            rows.append(row)

    if HAS_PANDAS:
        df = pd.DataFrame(rows, columns=CSV_FIELDS)
        df.drop_duplicates(inplace=True)
        df.to_csv(output_path, index=False, encoding="utf-8")
        log.info("pandas: wrote %d rows → %s", len(df), output_path)
    else:
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        log.info("csv: wrote %d rows → %s", len(rows), output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape cloud infrastructure metadata from public GitHub repos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python github_cloudInfra_scraper.py
  python github_cloudInfra_scraper.py --max-repos 50 --workers 8
  python github_cloudInfra_scraper.py --keywords "aws lambda" "gcp cloud run"
  python github_cloudInfra_scraper.py --use-graphql --output my_dataset.csv
  python github_cloudInfra_scraper.py --no-cache --verbose
        """,
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=DEFAULT_KEYWORDS,
        metavar="KW",
        help="Search keyword phrases (space-separated, quote multi-word)",
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        default=20,
        metavar="N",
        help="Max repos per keyword (default: 20)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=50,
        metavar="N",
        help="Max files to fetch per repo (default: 50)",
    )
    parser.add_argument(
        "--min-stars",
        type=int,
        default=50,
        metavar="N",
        help="Minimum star count filter (default: 50)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        metavar="N",
        help="Parallel worker threads for repo processing (default: 4)",
    )
    parser.add_argument(
        "--output",
        default="cloud_infra_github_dataset.csv",
        metavar="PATH",
        help="Output CSV file path (default: cloud_infra_github_dataset.csv)",
    )
    parser.add_argument(
        "--token",
        default=None,
        metavar="TOKEN",
        help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--use-graphql",
        action="store_true",
        help="Use GraphQL API for repository search (bonus feature)",
    )
    parser.add_argument(
        "--cache-dir",
        default=".scraper_cache",
        metavar="DIR",
        help="Directory for file-content cache (default: .scraper_cache)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable the file-content cache",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point for the cloud infrastructure scraper."""
    args = parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    log.info("=== GitHub Cloud Infrastructure Scraper ===")
    log.info("Output: %s | Workers: %d | Max repos/query: %d",
             args.output, args.workers, args.max_repos)

    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        log.warning(
            "GITHUB_TOKEN not set — anonymous API access is heavily rate-limited. "
            "Set GITHUB_TOKEN or pass --token for reliable results."
        )

    cache = None if args.no_cache else FileCache(args.cache_dir)
    client = GitHubClient(token=token, cache=cache)

    scraper = CloudInfraScraper(
        client=client,
        keywords=args.keywords,
        max_repos_per_query=args.max_repos,
        max_files_per_repo=args.max_files,
        min_stars=args.min_stars,
        workers=args.workers,
        use_graphql=args.use_graphql,
    )

    records = scraper.run()

    if not records:
        log.warning("No records collected. Check your token and search keywords.")
        sys.exit(1)

    write_csv(records, args.output)
    print(f"\nDone. {len(records)} records saved to '{args.output}'")


if __name__ == "__main__":
    main()
