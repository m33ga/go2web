# go2web

![PyPI version](https://img.shields.io/pypi/v/go2web.svg)

CLI for making requests and searching the web


## Features

- **`go2web fetch <url>`** — makes a raw HTTP/HTTPS request (no third-party library) and prints a clean, human-readable result inside a styled panel
- **`go2web search <query>`** — searches Bing and presents an interactive picker; select a result to immediately fetch and display it
- **Smart content rendering** — strips HTML tags, pretty-prints JSON, passes plain text through unchanged
- **Transparent redirect following** — each hop is logged to stderr so you always see where you end up
- **Local response cache** — responses are cached to `~/.go2web_cache.json` for 30 s, with `Cache-Control: no-store/no-cache` respected
- **Usable as a library** — `HTTPClient`, `CacheStore`, `ParserManager` and search engines are all importable

---

## Installation

go2web is a standalone CLI tool. Install it globally so it's available everywhere — no virtual environment needed.

```sh
# Recommended — uv (fastest, isolated)
uv tool install go2web

# pipx (isolated, widely available)
pipx install go2web

# pip (global, no isolation)
pip install go2web
```

Requires Python 3.12+. See [full installation docs](https://m33ga.github.io/go2web/installation/).

> **Tip:** `uv tool install` and `pipx install` both create an isolated environment
> for go2web so it never conflicts with your project dependencies.

---

## Quick start

```sh
go2web fetch https://example.com
go2web search python asyncio tutorial
```

---

## CLI usage

```
go2web --help                       # show help
go2web fetch <URL>                  # fetch a URL and print human-readable output
go2web search <term …>              # search the web and pick a result interactively
```

The `https://` scheme prefix is optional — go2web adds it automatically.

```sh
go2web fetch example.com            # same as https://example.com
go2web search "best pizza recipes"
```

See [full CLI & usage docs](https://m33ga.github.io/go2web/usage/).

---

## Using as a library

go2web can also be used as a Python library. Add it to your project:

```sh
uv add go2web   # or: pip install go2web
```

```python
from go2web.http.client import HTTPClient
from go2web.http.parsers.parser_manager import ParserManager

client = HTTPClient()
response = client.get("https://httpbin.org/json")

parser = ParserManager().get_parser(response.get_content_type())
print(parser.parse(response.body))
```

See [API reference](https://m33ga.github.io/go2web/api/).

---

## Documentation

Built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

| | |
|---|---|
| Live docs | <https://m33ga.github.io/go2web/> |
| Local preview | `just docs-serve` → <http://localhost:8000> |
| Build | `just docs-build` |

---

## Development

```sh
git clone https://github.com/m33ga/go2web
cd go2web
uv tool install --editable .   # installs CLI with live updates

uv run pytest                  # tests
just qa                        # format + lint + type check + test
```

---

## Links

- **GitHub:** <https://github.com/m33ga/go2web>
- **PyPI:** <https://pypi.org/project/go2web/>
- **Author:** [Mihai Gurduza](https://github.com/m33ga)
- **License:** MIT