from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from go2web.http.client import HTTPClient
from go2web.search.engines.base import BaseSearchEngine
from go2web.search.result import SearchResult


class BingEngine(BaseSearchEngine):
    BASE_URL = "https://www.bing.com/search?q={query}"

    def __init__(self, client: HTTPClient | None = None) -> None:
        self._client = client or HTTPClient()

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        url = self.BASE_URL.format(query=quote_plus(query))
        response = self._client.get(url)
        return self._parse(response.body, limit)

    def _parse(self, html: str, limit: int) -> list[SearchResult]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for i, result in enumerate(soup.select("li.b_algo")[:limit]):
            title_el = result.select_one("h2 a")

            if not title_el:
                continue

            results.append(
                SearchResult(
                    rank=i + 1,
                    title=title_el.get_text(strip=True),
                    url=title_el.get("href", ""),
                )
            )

        return results
