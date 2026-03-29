"""Persistent JSON cache for HTTP responses.

Responses are stored keyed by URL in a single JSON file on disk
(default: ``~/.go2web_cache.json``). Each entry carries an ``expires_at``
timestamp so stale entries are pruned on the next read.

Example:
    >>> from go2web.cache.store import CacheStore
    >>> cache = CacheStore()
    >>> cache.set("https://example.com", 200, {"content-type": "text/html"}, "<html>…</html>")
    >>> entry = cache.get("https://example.com")
    >>> entry.status
    200
"""

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from go2web.console import print_info

CACHE_FILE = Path.home() / ".go2web_cache.json"


@dataclass
class CacheEntry:
    """A single cached HTTP response.

    Attributes:
        body: The decoded response body.
        status: The HTTP status code at the time of caching.
        headers: Response headers (lower-cased keys).
        expires_at: Unix timestamp after which this entry is considered stale.
    """

    body: str
    status: int
    headers: dict[str, str]
    expires_at: float


class CacheStore:
    """A file-backed key/value store for HTTP responses.

    Entries are keyed by URL and serialised as JSON to *cache_file*.
    Expired entries are evicted lazily on read. The store respects
    ``Cache-Control: no-store`` and ``no-cache`` directives — responses
    carrying these headers are never persisted.

    Attributes:
        DEFAULT_TTL: Default time-to-live in seconds (``30``).

    Example:
        Using a temporary cache file:

        >>> from pathlib import Path
        >>> from go2web.cache.store import CacheStore
        >>> cache = CacheStore(cache_file=Path("/tmp/test_cache.json"))
        >>> cache.set("https://example.com", 200, {}, "hello")
        >>> cache.get("https://example.com").body
        'hello'
        >>> cache.clear()
    """

    DEFAULT_TTL = 30

    def __init__(self, cache_file: Path = CACHE_FILE) -> None:
        """Initialise the store, loading existing entries from *cache_file*.

        Args:
            cache_file: Path to the JSON file used for persistence. Created
                on the first :meth:`set` call if it does not exist.
        """
        self._file = cache_file
        self._store: dict[str, CacheEntry] = self._load()

    def get(self, url: str) -> CacheEntry | None:
        """Return the cached entry for *url*, or ``None`` if missing or expired.

        A dim info message is printed to stderr when a valid entry is returned.

        Args:
            url: The exact URL used as the cache key.

        Returns:
            A :class:`CacheEntry` if a fresh entry exists, otherwise ``None``.
        """
        entry = self._store.get(url)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._store[url]
            return None
        print_info("Entry retrieved from cache.")
        return entry

    def set(self, url: str, status: int, headers: dict[str, str], body: str) -> None:
        """Store a response in the cache and persist to disk.

        The entry is **not** stored when the server sends
        ``Cache-Control: no-store`` or ``no-cache``.

        Args:
            url: Cache key — should be the final (post-redirect) URL.
            status: HTTP status code of the response.
            headers: Response headers (lower-cased keys).
            body: Decoded response body.
        """
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
        """Remove all cached entries and delete the cache file from disk."""
        self._store.clear()
        self._file.unlink(missing_ok=True)

    def _parse_ttl(self, headers: dict[str, str]) -> int:
        """Return the TTL in seconds based on *Cache-Control* headers.

        Returns ``0`` when the server explicitly forbids caching, otherwise
        :attr:`DEFAULT_TTL`.
        """
        cc = headers.get("cache-control", "")

        if "no-store" in cc or "no-cache" in cc:
            return 0

        return self.DEFAULT_TTL

    def _load(self) -> dict[str, CacheEntry]:
        """Load entries from the JSON file, returning an empty dict if absent."""
        if not self._file.exists():
            return {}
        raw = json.loads(self._file.read_text(encoding="utf-8"))
        return {k: CacheEntry(**v) for k, v in raw.items()}

    def _persist(self) -> None:
        """Serialise the in-memory store to disk."""
        self._file.write_text(
            json.dumps({k: asdict(v) for k, v in self._store.items()}, ensure_ascii=False),
            encoding="utf-8",
        )
