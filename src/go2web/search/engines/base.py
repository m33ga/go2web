from abc import ABC, abstractmethod

from go2web.search.result import SearchResult


class BaseSearchEngine(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[SearchResult]: ...
