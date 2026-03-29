"""Data class representing a single search result."""

from dataclasses import dataclass


@dataclass
class SearchResult:
    """A single search engine result.

    Attributes:
        rank: 1-based position on the results page.
        title: The page title as displayed in search results.
        url: The destination URL after Bing tracking is decoded.

    Example:
        >>> from go2web.search.result import SearchResult
        >>> r = SearchResult(rank=1, title="Python.org", url="https://python.org")
        >>> r.rank
        1
    """

    rank: int
    title: str
    url: str
