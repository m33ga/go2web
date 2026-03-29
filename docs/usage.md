# Usage

## CLI reference

| Command | Description |
|---|---|
| `go2web --help` | Show help and exit |
| `go2web fetch <URL>` | Fetch a URL and print human-readable output |
| `go2web search <term …>` | Search the web and pick a result interactively |

> **Tip:** You can omit `https://` — go2web will add it automatically.

---

## Fetching a URL

```bash
go2web fetch https://example.com
go2web fetch example.com          # https:// prefix is added automatically
go2web fetch http://example.com   # plain HTTP also works
```

The response is printed inside a unicode border, with all HTML tags stripped
and JSON pretty-printed. Plain-text responses are passed through unchanged.

If the server redirects, each hop is shown on stderr before the final
response is printed:

```
Redirect 301 Moved Permanently  http://example.com
                              → https://example.com
```

Responses are cached in `~/.go2web_cache.json` for 30 seconds by default.
A dim `Entry retrieved from cache.` notice appears on stderr when a cached
entry is used.

---

## Searching the web

```bash
go2web search python asyncio
go2web search "best pizza recipes"
```

go2web queries Bing and shows the top 10 results in an interactive picker.
Use arrow keys to select a result and press **Enter** to fetch and display it,
or choose **Cancel** to exit.

---

## Using as a library

All of go2web's internals are importable. You can use the HTTP client,
cache store, content parsers, and search engines independently.

### Fetching a URL

```python
from go2web.http.client import HTTPClient

client = HTTPClient()
response = client.get("https://httpbin.org/json")
print(response.status, response.reason)
print(response.body)
```

### Parsing the response body

```python
from go2web.http.client import HTTPClient
from go2web.http.parsers.parser_manager import ParserManager

client = HTTPClient()
response = client.get("https://example.com")

parser = ParserManager().get_parser(response.get_content_type())
print(parser.parse(response.body))
```

### Disabling the cache

```python
client = HTTPClient(use_cache=False)
```

### Using a custom cache location

```python
from pathlib import Path
from go2web.cache.store import CacheStore
from go2web.http.client import HTTPClient

cache = CacheStore(cache_file=Path("/tmp/my_cache.json"))
client = HTTPClient(cache=cache)
```

### Searching programmatically

```python
from go2web.search.engines.bing import BingEngine

engine = BingEngine()
results = engine.search("python packaging", limit=5)
for r in results:
    print(r.rank, r.title, r.url)
```

### Using a custom search engine

```python
from go2web.search.engines.base import BaseSearchEngine
from go2web.search.result import SearchResult


class DuckDuckGoEngine(BaseSearchEngine):
    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        # your implementation
        ...
```

Pass it to `Searcher`:

```python
from go2web.commands.search import Searcher

searcher = Searcher(engine=DuckDuckGoEngine())
searcher.search("linux kernel")
```
