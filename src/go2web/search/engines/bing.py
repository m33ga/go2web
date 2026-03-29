"""Bing search engine backend."""

from base64 import b64decode
from urllib.parse import parse_qs, quote_plus, urlparse

from bs4 import BeautifulSoup

from go2web.http.client import HTTPClient
from go2web.search.engines.base import BaseSearchEngine
from go2web.search.result import SearchResult


class BingEngine(BaseSearchEngine):
    """Search engine backend powered by Bing.

    Fetches the Bing search results page for a given query and scrapes
    the top organic results. Bing encodes destination URLs in a base64
    tracking wrapper — this is decoded transparently so callers always
    receive the real destination URL.

    Attributes:
        BASE_URL: Bing search URL template. ``{query}`` is replaced with
            the URL-encoded query string.

    Example:
        >>> from go2web.search.engines.bing import BingEngine
        >>> engine = BingEngine()
        >>> results = engine.search("python packaging", limit=3)
        >>> for r in results:
        ...     print(r.rank, r.title)
    """

    BASE_URL = "https://www.bing.com/search?q={query}"

    def __init__(self, client: HTTPClient | None = None) -> None:
        """Initialise the engine.

        Args:
            client: An :class:`~go2web.http.client.HTTPClient` instance used
                to fetch the Bing results page. A default client (with caching
                enabled) is created when *client* is ``None``.
        """
        self._client = client or HTTPClient()

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Query Bing and return up to *limit* organic results.

        Args:
            query: The search query string.
            limit: Maximum number of results to return (default ``10``).

        Returns:
            A list of :class:`~go2web.search.result.SearchResult` objects
            ordered by their position on the results page.
        """
        url = self.BASE_URL.format(query=quote_plus(query))
        response = self._client.get(url)
        return self._parse(response.body, limit)

    def _parse(self, html: str, limit: int) -> list[SearchResult]:
        """Scrape *html* for Bing result entries and return up to *limit* items."""
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for i, result in enumerate(soup.select("li.b_algo")[:limit]):
            title_el = result.select_one("h2 a")

            if not title_el:
                continue

            href = title_el.get("href")

            if not isinstance(href, str):
                continue

            url = self._extract_url(href)

            results.append(
                SearchResult(
                    rank=i + 1,
                    title=title_el.get_text(strip=True),
                    url=url,
                )
            )

        return results

    def _extract_url(self, href: str) -> str:
        """Decode a Bing tracking URL into the real destination URL.

        Bing wraps destination URLs in a query parameter ``u`` that is
        base64-encoded with an ``a1`` prefix. When this pattern is detected
        the prefix is stripped and the remainder is decoded. Falls back to
        returning *href* unchanged when the pattern does not match.

        Args:
            href: The raw ``href`` value from a Bing result anchor tag.

        Returns:
            The decoded destination URL, or *href* itself as a fallback.
        """
        qs = parse_qs(urlparse(href).query)
        raw = qs.get("u", [None])[0]
        if raw and raw.startswith("a1"):
            # strip the "a1" prefix and base64-decode
            return b64decode(raw[2:] + "==").decode("utf-8", errors="replace")
        return href
