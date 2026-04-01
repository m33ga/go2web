"""Low-level HTTP client built on raw sockets.

No third-party HTTP library is used. The client opens a TCP (or TLS-wrapped)
socket, sends a minimal HTTP/1.1 GET request, reads the response, and returns
a :class:`Response` object. Chunked transfer-encoding and automatic redirect
following are supported.

Example:
    >>> from go2web.http.client import HTTPClient
    >>> client = HTTPClient()
    >>> response = client.get("https://httpbin.org/json")
    >>> print(response.status)
    200
"""

import socket
import ssl
from dataclasses import dataclass
from urllib.parse import urlparse

from go2web.cache.store import CacheStore
from go2web.console import print_redirect


@dataclass
class Response:
    """A parsed HTTP response.

    Attributes:
        status: The HTTP status code (e.g. ``200``, ``404``).
        reason: The human-readable status phrase (e.g. ``"OK"``).
        headers: Response headers with lower-cased keys for easy lookup.
        body: The decoded response body as a string.
    """

    status: int
    reason: str
    headers: dict[str, str]
    body: str

    def get_content_type(self) -> str:
        """Return the value of the ``Content-Type`` header.

        Returns:
            The content-type string (e.g. ``"text/html; charset=utf-8"``),
            or an empty string if the header is absent.
        """
        return self.headers.get("content-type", "")

    def is_redirect(self) -> bool:
        """Return ``True`` if the status code indicates a redirect.

        The following codes are treated as redirects:
        301, 302, 303, 307, 308.
        """
        return self.status in (301, 302, 303, 307, 308)

    def redirect_url(self) -> str | None:
        """Return the URL from the ``Location`` header, or ``None`` if absent."""
        return self.headers.get("location")


class HTTPError(Exception):
    """Raised when a non-recoverable HTTP or network error occurs.

    Examples include redirect loops, too many redirects, unsupported URL
    schemes, or a missing ``Location`` header on a redirect response.
    """


class HTTPClient:
    """A simple, cache-aware HTTP client using raw sockets.

    All requests are made with HTTP/1.1 GET. TLS is supported for ``https://``
    URLs. Responses are optionally cached in a :class:`~go2web.cache.store.CacheStore`.

    Attributes:
        DEFAULT_TIMEOUT: Socket timeout in seconds (default ``10``).
        MAX_REDIRECTS: Maximum number of redirects to follow before raising
            :class:`HTTPError` (default ``10``).
        BUFFER_SIZE: Read buffer size in bytes (default ``4096``).

    Example:
        Fetching a URL with caching disabled:

        >>> client = HTTPClient(use_cache=False)
        >>> response = client.get("https://example.com")
        >>> print(response.status)
        200

        Using a custom cache location:

        >>> from pathlib import Path
        >>> from go2web.cache.store import CacheStore
        >>> cache = CacheStore(cache_file=Path("/tmp/my_cache.json"))
        >>> client = HTTPClient(cache=cache)
    """

    DEFAULT_TIMEOUT = 10
    MAX_REDIRECTS = 10
    BUFFER_SIZE = 4096

    def __init__(self, cache: CacheStore | None = None, use_cache: bool = True) -> None:
        """Initialise the client.

        Args:
            cache: A :class:`~go2web.cache.store.CacheStore` instance to use.
                A default store backed by ``~/.go2web_cache.json`` is created
                when *cache* is ``None``.
            use_cache: Set to ``False`` to bypass both reading from and writing
                to the cache.
        """
        self._cache = cache or CacheStore()
        self._use_cache = use_cache

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Prepend ``https://`` to *url* when no scheme is present."""
        parsed = urlparse(url)

        if not parsed.scheme:
            return f"https://{url}"

        return url

    def get(self, url: str, *, follow_redirects: bool = True) -> Response:
        """Perform an HTTP GET request, following redirects by default.

        The cache is checked before issuing a network request. On a cache
        miss, the live response is stored (unless caching is disabled or the
        server sends ``Cache-Control: no-store``).

        Args:
            url: The URL to fetch. A missing ``https://`` scheme is added
                automatically.
            follow_redirects: When ``True`` (the default), 3xx responses are
                followed automatically up to :attr:`MAX_REDIRECTS` hops.

        Returns:
            A :class:`Response` for the final (non-redirect) response.

        Raises:
            HTTPError: On redirect loops, too many redirects, unsupported
                schemes, or a redirect with no ``Location`` header.

        Example:
            >>> client = HTTPClient()
            >>> response = client.get("example.com")   # https:// added automatically
            >>> response.status
            200
        """
        visited = set()
        current_url = self._normalize_url(url)

        while True:
            if current_url in visited:
                raise HTTPError(f"Error: Redirect loop detected at {current_url}")
            if len(visited) >= self.MAX_REDIRECTS:
                raise HTTPError(f"Error: Too many redirects (max {self.MAX_REDIRECTS})")

            visited.add(current_url)

            if self._use_cache:
                cached = self._cache.get(current_url)
                if cached:
                    return Response(
                        status=cached.status,
                        reason="",
                        headers=cached.headers,
                        body=cached.body,
                    )

            response = self._do_get(current_url)

            if follow_redirects and response.is_redirect():
                location = response.redirect_url()
                if not location:
                    raise HTTPError("Error: Redirect with no Location header")
                print_redirect(response.status, response.reason, current_url, location)
                # handle relative redirects
                if location.startswith("/"):
                    parsed = urlparse(current_url)
                    location = f"{parsed.scheme}://{parsed.netloc}{location}"
                current_url = location
                continue

            if self._use_cache and response.status < 400:
                self._cache.set(current_url, response.status, response.headers, response.body)
            break
        return response

    def _do_get(self, url: str) -> Response:
        """Issue a single (non-redirect-aware) GET request to *url*."""
        parsed = urlparse(url)

        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https"):
            raise HTTPError(f"Unsupported scheme: {scheme}")

        https = scheme == "https"
        host = parsed.hostname
        if host is None:
            raise ValueError(f"Invalid URL, missing hostname: {url}")
        port = parsed.port or (443 if https else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"

        sock = self._open_socket(host, port, https)
        try:
            request = self._build_request(host, path)
            sock.sendall(request.encode("utf-8"))
            raw = self._read_response(sock)
        finally:
            sock.close()

        return self._parse_response(raw)

    def _open_socket(self, host: str, port: int, https: bool) -> socket.socket:
        """Open a TCP socket, wrapping it in TLS when *https* is ``True``."""
        sock = socket.create_connection((host, port), timeout=self.DEFAULT_TIMEOUT)
        if https:
            ctx = ssl.create_default_context()
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            sock = ctx.wrap_socket(sock, server_hostname=host)
        return sock

    def _build_request(self, host: str, path: str) -> str:
        """Build a minimal HTTP/1.1 GET request string."""
        lines = [
            f"GET {path} HTTP/1.1",
            f"Host: {host}",
            "Accept: text/html,application/json,*/*",
            "Accept-Encoding: identity",  # no compression - no problemasion
            "Connection: close",
            "",
            "",
        ]
        return "\r\n".join(lines)

    def _read_response(self, sock: socket.socket) -> bytes:
        """Read the full response from *sock* into a single bytes object."""
        chunks = []
        while True:
            chunk = sock.recv(self.BUFFER_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)

    def _parse_response(self, raw: bytes) -> Response:
        """Parse raw response bytes into a :class:`Response`."""
        # split headers from body on the first blank line
        header_section, _, body_bytes = raw.partition(b"\r\n\r\n")
        header_lines = header_section.decode("utf-8", errors="replace").split("\r\n")

        # status line
        status_line = header_lines[0]
        parts = status_line.split(" ", 2)
        status = int(parts[1])
        reason = parts[2] if len(parts) > 2 else ""

        # headers — lowercase keys for easy lookup
        headers: dict[str, str] = {}
        for line in header_lines[1:]:
            if ":" in line:
                key, _, value = line.partition(":")
                headers[key.strip().lower()] = value.strip()

        # unchunk if needed
        if headers.get("transfer-encoding", "").lower() == "chunked":
            body_bytes = self._decode_chunked(body_bytes)

        # decode body
        body = body_bytes.decode("utf-8", errors="replace")

        return Response(status=status, reason=reason, headers=headers, body=body)

    def _decode_chunked(self, data: bytes) -> bytes:
        """Strip chunk-size lines and reassemble a chunked response body."""
        result = []
        while data:
            # find the end of the chunk-size line
            crlf = data.find(b"\r\n")
            if crlf == -1:
                break
            size_str = data[:crlf].split(b";")[0]  # ignore chunk extensions
            try:
                chunk_size = int(size_str.strip(), 16)
            except ValueError:
                break
            if chunk_size == 0:
                break
            start = crlf + 2
            result.append(data[start : start + chunk_size])
            data = data[start + chunk_size + 2 :]  # skip trailing \r\n
        return b"".join(result)
