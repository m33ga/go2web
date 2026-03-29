# Cache

Responses are cached to `~/.go2web_cache.json` using a simple TTL-based
key/value store. The cache respects `Cache-Control: no-store` and `no-cache`.

## CacheStore

::: go2web.cache.store.CacheStore

## CacheEntry

::: go2web.cache.store.CacheEntry
