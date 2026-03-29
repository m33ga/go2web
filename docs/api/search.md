# Search

The search layer abstracts web search engines behind a common interface.
`BingEngine` is the built-in backend; custom engines can be plugged in by
subclassing `BaseSearchEngine`.

## BingEngine

::: go2web.search.engines.bing.BingEngine

## SearchResult

::: go2web.search.result.SearchResult

## BaseSearchEngine *(abstract)*

::: go2web.search.engines.base.BaseSearchEngine
