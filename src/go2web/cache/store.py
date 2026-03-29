import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from go2web.console import print_info

CACHE_FILE = Path.home() / ".go2web_cache.json"


@dataclass
class CacheEntry:
    body: str
    status: int
    headers: dict[str, str]
    expires_at: float


class CacheStore:
    DEFAULT_TTL = 30

    def __init__(self, cache_file: Path = CACHE_FILE) -> None:
        self._file = cache_file
        self._store: dict[str, CacheEntry] = self._load()

    def get(self, url: str) -> CacheEntry | None:
        entry = self._store.get(url)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._store[url]
            return None
        print_info("Entry retrieved from cache.")
        return entry

    def set(self, url: str, status: int, headers: dict[str, str], body: str) -> None:
        ttl = self._parse_ttl(headers)
        if ttl == 0:
            return
        self._store[url] = CacheEntry(
            body=body,
            status=status,
            headers=headers,
            expires_at=time.time() + ttl,
        )
        self._persist()

    def clear(self) -> None:
        self._store.clear()
        self._file.unlink(missing_ok=True)

    def _parse_ttl(self, headers: dict[str, str]) -> int:
        cc = headers.get("cache-control", "")

        if "no-store" in cc or "no-cache" in cc:
            return 0

        return self.DEFAULT_TTL

    def _load(self) -> dict[str, CacheEntry]:
        if not self._file.exists():
            return {}
        raw = json.loads(self._file.read_text(encoding="utf-8"))
        return {k: CacheEntry(**v) for k, v in raw.items()}

    def _persist(self) -> None:
        self._file.write_text(
            json.dumps({k: asdict(v) for k, v in self._store.items()}, ensure_ascii=False),
            encoding="utf-8",
        )
