from dataclasses import dataclass


@dataclass
class SearchResult:
    rank: int
    title: str
    url: str
