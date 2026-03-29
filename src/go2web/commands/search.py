"""High-level search command — queries a search engine and drives an interactive picker."""

import questionary
from questionary import Choice

from go2web.commands.fetch import Fetcher
from go2web.console import print_error, print_info
from go2web.search.engines.base import BaseSearchEngine
from go2web.search.engines.bing import BingEngine
from go2web.search.result import SearchResult


class Searcher:
    """Search the web and interactively open a result.

    Combines a :class:`~go2web.search.engines.base.BaseSearchEngine` with a
    :class:`~go2web.commands.fetch.Fetcher` to implement the full
    ``go2web search`` workflow:

    1. Query the search engine.
    2. Present results in a ``questionary`` interactive picker.
    3. Fetch and display the selected result.

    The engine and fetcher are injected so they can be swapped in tests or
    extended for custom workflows.

    Example:
        Using the default Bing engine:

        >>> from go2web.commands.search import Searcher
        >>> Searcher().search("python packaging")

        Using a custom engine and disabling the fetcher cache:

        >>> from go2web.commands.fetch import Fetcher
        >>> from go2web.search.engines.bing import BingEngine
        >>> Searcher(engine=BingEngine(), fetcher=Fetcher(use_cache=False)).search("python")
    """

    def __init__(
        self,
        engine: BaseSearchEngine | None = None,
        fetcher: Fetcher | None = None,
        limit: int = 10,
    ) -> None:
        """Initialise the searcher.

        Args:
            engine: The search engine backend to use. Defaults to
                :class:`~go2web.search.engines.bing.BingEngine`.
            fetcher: The fetcher used to open the selected result. Defaults to
                a :class:`~go2web.commands.fetch.Fetcher` with caching enabled.
            limit: Number of results to request from the engine (default ``10``).
        """
        self._engine = engine or BingEngine()
        self._fetcher = fetcher or Fetcher()
        self._limit = limit

    def search(self, query: str, limit: int | None = None) -> None:
        """Run a search for *query* and open the chosen result.

        Prints an interactive picker to the terminal. If the user selects a
        result, it is fetched and displayed via :meth:`~go2web.commands.fetch.Fetcher.fetch`.
        Choosing **Cancel** exits without fetching.

        Args:
            query: The search query string.
            limit: Override the instance-level result limit for this call.
        """
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
        """Display an interactive picker and return the chosen result.

        Args:
            results: The list of search results to display.

        Returns:
            The selected :class:`~go2web.search.result.SearchResult`, or
            ``None`` when the user chooses **Cancel** or exits.
        """
        choices = [Choice(title=f"{r.rank:>2}. {r.title}  {r.url}", value=r) for r in results]
        choices.append(Choice(title="Cancel", value=""))

        return questionary.select(
            "Select a result to open:",
            choices=choices,
        ).ask()
