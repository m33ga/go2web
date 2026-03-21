from go2web.commands.fetch import Fetcher
from go2web.search.engines.base import BaseSearchEngine
from go2web.search.engines.bing import BingEngine


class Searcher:
    def __init__(
        self,
        engine: BaseSearchEngine | None = None,
        fetcher: Fetcher | None = None,
        limit: int = 10,
    ) -> None:
        self._engine = engine or BingEngine()
        self._fetcher = fetcher or Fetcher()
        self._limit = limit

    def search(self, query: str, limit: int | None = None) -> None:
        results = self._engine.search(query, limit=limit or self._limit)

        if not results:
            print("No results found.")
            return

        print(results)
