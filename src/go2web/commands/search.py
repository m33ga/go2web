import questionary
from questionary import Choice

from go2web.commands.fetch import Fetcher
from go2web.console import print_error, print_info
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
        try:
            results = self._engine.search(query, limit=limit or self._limit)
        except Exception as exc:
            print_error(f"Search failed: {exc}")
            raise SystemExit(1) from exc

        if not results:
            print_info("No results found.")
            return

        selected = self._prompt(results)

        if not selected:
            return

        print_info(f"Fetching: {selected.url}")
        self._fetcher.fetch(selected.url)

    def _prompt(self, results: list[SearchResult]) -> SearchResult | None:
        choices = [Choice(title=f"{r.rank:>2}. {r.title}  {r.url}", value=r) for r in results]
        choices.append(Choice(title="Cancel", value=""))

        return questionary.select(
            "Select a result to open:",
            choices=choices,
        ).ask()
