# NewsAPI

Verified on `2026-03-25`.

## Local Usage

- [news.py](../../../src/solstein/data/sources/news.py)
- [news_signal_detector.py](../../../src/solstein/data/connectors/news_signal_detector.py)
- [newsapi.py](../../../src/solstein/connectors/news/newsapi.py)

## Official Surfaces

- Docs: `https://newsapi.org/docs`
- `llms.txt`: `https://newsapi.org/llms.txt` returned `404` in this pass
- `robots.txt`: `https://newsapi.org/robots.txt`

Confirmed during this pass:

- the docs site is live
- the root `robots.txt` is present
- the root `llms.txt` was not present in the first pass

## Good Patterning

- Keep NewsAPI as the primary structured news source when configured.
- Bound retrieval by explicit date range, page size, and query intent.
- Mark Google or DuckDuckGo fallbacks as lower-confidence search-derived evidence, not equivalent NewsAPI payloads.
- Preserve source name, article URL, publication date, and derived sentiment separately.
- Deduplicate article URLs before creating downstream facts.

## Caveats

- Plan limits and archive coverage vary materially by account tier.
- The current repo mixes a structured API path with HTML search fallbacks.
- `robots.txt` disallows `/v1/` and `/v2/`, which is a reminder not to treat direct endpoint scraping as a docs retrieval strategy.

## Test Gates

- NewsAPI success payload normalization
- empty-article and quota-exhaustion fallback paths
- duplicate-URL suppression
- schema validation for `PressCoverage` and `NewsArticle`
