import questionary
from questionary import Choice

from go2web.commands.fetch import Fetcher
from go2web.search.engines.base import BaseSearchEngine
from go2web.search.engines.bing import BingEngine
from go2web.search.result import SearchResult


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

        selected = self._prompt(results)

        if not selected:
            return

        self._open(selected)

    def _prompt(self, results: list[SearchResult]) -> SearchResult | None:
        choices = [Choice(title=f"{r.rank:>2}. {r.title}  {r.url}", value=r) for r in results]
        choices.append(Choice(title="Cancel", value=""))

        return questionary.select(
            "Select a result to open:",
            choices=choices,
        ).ask()

    def _open(self, result: SearchResult) -> None:
        print(f"\nFetching: {result.url}\n")
        fetched = self._fetcher.fetch(result.url)
        print(fetched)
