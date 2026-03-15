import socket
import ssl
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class Response:
    status: int
    reason: str
    headers: dict[str, str]
    body: str

    def get_content_type(self) -> str:
        return self.headers["content-type"]

    def get_status(self) -> int:
        return self.status

    def is_redirect(self) -> bool:
        return self.status in (301, 302, 303, 307, 308)

    def redirect_url(self) -> str | None:
        return self.headers.get("location")


class HTTPError(Exception):
    pass


class HTTPClient:
    DEFAULT_TIMEOUT = 10
    MAX_REDIRECTS = 10
    BUFFER_SIZE = 4096

    def get(self, url: str, *, follow_redirects: bool = True) -> Response:
        visited = set()
        current_url = url

        while True:
            if current_url in visited:
                raise HTTPError(f"Error: Redirect loop detected at {current_url}")
            if len(visited) >= self.MAX_REDIRECTS:
                raise HTTPError(f"Error: Too many redirects (max {self.MAX_REDIRECTS})")

            visited.add(current_url)
            response = self._do_get(current_url)

            if follow_redirects and response.is_redirect():
                location = response.redirect_url()
                if not location:
                    raise HTTPError("Error: Redirect with no Location header")
                # handle relative redirects
                if location.startswith("/"):
                    parsed = urlparse(current_url)
                    location = f"{parsed.scheme}://{parsed.netloc}{location}"
                current_url = location
                continue

        return response

    def _do_get(self, url: str) -> Response:
        parsed = urlparse(url)

        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https"):
            raise ValueError(f"Unsupported scheme: {scheme}")

        https = scheme == "https"
        host = parsed.hostname
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
        sock = socket.create_connection((host, port), timeout=self.DEFAULT_TIMEOUT)
        if https:
            ctx = ssl.create_default_context()
            sock = ctx.wrap_socket(sock, server_hostname=host)
        return sock

    def _build_request(self, host: str, path: str) -> str:
        lines = [
            f"GET {path} HTTP/1.1",
            f"Host: {host}",
            "Accept: text/html,application/json,*/*",
            "Accept-Encoding: identity",  # no compresion - no problemasion
            "Connection: close",
            "",
            "",
        ]
        return "\r\n".join(lines)

    def _read_response(self, sock: socket.socket) -> bytes:
        chunks = []
        while True:
            chunk = sock.recv(self.BUFFER_SIZE)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)

    def _parse_response(self, raw: bytes) -> Response:
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
        """Strip chunk size lines and reassemble the body."""
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
