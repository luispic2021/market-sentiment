# Changelog

## 2026-06-20: v0.5 Model retirement fix

### Fixed
- Updated the default Anthropic model from retired `claude-opus-4-20250514` to active `claude-opus-4-8`, matching Anthropic's recommended replacement after the June 15, 2026 retirement.
- Added top-level exception logging so API/model failures are written to `market_sentiment_debug.log` and no longer fail silently.
- Added HTTP timeout and status checks when fetching the Schwab article.

### Improved
- Added `ANTHROPIC_MODEL` and `OPENAI_MODEL` environment overrides.

## 2025-08-03: v0.4 Anthropic Model upgrade

### Features
* Upgraded to Claude Opus 4 (`claude-opus-4-20250514`) to improve comprehension and response quality in sentiment analysis, as current usage analysis showed no correlation between the provided sentiment and the actual market direction.

## 2025-04-11: Alpha Version

### Features
- Enhanced `extract_publish_datetime()` to return both a machine-readable date (`YYYY-MM-DD`) for internal validation and the full raw publish timestamp for logging and push notifications.
- Logged the publish date as extracted directly from the Schwab article HTML to improve traceability and debugability.
- Captured the complete raw LLM response and stored it in the CSV sentiment log for transparency and post-analysis.
- Improved sentiment validation by comparing only the date portion of the publish timestamp (ignoring time) for resilience across time zones and format variations.
- Introduced a structured debug log (`market_sentiment_debug.log`) supporting multiple log levels (`INFO`, `DEBUG`, `WARNING`) to assist in troubleshooting.
- Added a configurable `LOG_LEVEL` environment variable, allowing developers to toggle verbosity without changing code.
- Implemented article content hashing (MD5) to detect duplicate articles across runs and prevent redundant LLM evaluations.
- Integrated Claude 3.5 Sonnet (`claude-3-5-sonnet-20241022`) as the default model for sentiment analysis via Anthropic API.

---

## 2025-04-21: Bugfix Release

### Fixed
- Updated the regex used for extracting the publish date to correctly include the year component (`April 17, 2025`) rather than truncating at the first comma (e.g., `April 17`), which had caused parsing failures.

---

## 2025-05-02: Beta Version

### Features
- Upgraded to Claude 3.7 Sonnet (`claude-3-7-sonnet-20250219`) to improve comprehension and response quality in sentiment analysis.
- Increased the response token limit (`max_tokens`) to 256 to enable longer, multi-line responses that include sentiment plus reasoning.
- Push notifications now include both the high-level sentiment and a concise explanation (truncated at 400 characters for Pushover compatibility) to provide richer, actionable context.
- Refactored `clean_sentiment()` to extract only the first word of the LLM response, ensuring robust parsing of the sentiment label even when the output includes detailed commentary.
