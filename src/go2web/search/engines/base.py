"""Abstract base class for search engine backends."""

from abc import ABC, abstractmethod

from go2web.search.result import SearchResult


class BaseSearchEngine(ABC):
    """Interface for web search engine backends.

    Subclass :class:`BaseSearchEngine` to add support for a new search
    provider. The only required method is :meth:`search`.

    Example:
        A minimal custom engine:

        >>> from go2web.search.engines.base import BaseSearchEngine
        >>> from go2web.search.result import SearchResult
        >>>
        >>> class MyEngine(BaseSearchEngine):
        ...     def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        ...         return [SearchResult(rank=1, title="Example", url="https://example.com")]
    """

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Search for *query* and return up to *limit* results.

        Args:
            query: The search query string.
            limit: Maximum number of results to return.

        Returns:
            A list of :class:`~go2web.search.result.SearchResult` objects,
            ordered by relevance rank.
        """
        ...
