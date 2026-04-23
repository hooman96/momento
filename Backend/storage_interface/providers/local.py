"""Local filesystem backend. Useful for development and unit tests."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from ..base import ObjectInfo, StorageProvider
from ..exceptions import ObjectNotFoundError


class LocalStorageProvider(StorageProvider):
    """Stores each key as a file under `root`.

    Nested prefixes (e.g. `runs/42/out.log`) are represented as subdirectories.
    """

    def __init__(self, root: str):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        if not key:
            raise ValueError(f"invalid key: {key!r}")
        candidate = (self.root / key).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"invalid key: {key!r}") from exc
        return candidate

    def put(self, key: str, value: bytes, content_type: Optional[str] = None) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value)

    def get(self, key: str) -> bytes:
        path = self._path(key)
        if not path.is_file():
            raise ObjectNotFoundError(key)
        return path.read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if not path.is_file():
            raise ObjectNotFoundError(key)
        path.unlink()

    def list(self, prefix: str = "") -> List[ObjectInfo]:
        base = self.root
        results: List[ObjectInfo] = []
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(base).as_posix()
            if rel.startswith(prefix):
                stat = p.stat()
                results.append(
                    ObjectInfo(
                        key=rel,
                        size=stat.st_size,
                        last_modified=datetime.fromtimestamp(
                            stat.st_mtime, tz=timezone.utc
                        ).isoformat(),
                    )
                )
        results.sort(key=lambda o: o.key)
        return results

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()
