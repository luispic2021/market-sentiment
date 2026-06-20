# Market Sentiment Checker

This Python script fetches the latest stock market update from [Schwab's daily open report](https://www.schwab.com/learn/story/stock-market-update-open), analyzes it using a language model (OpenAI or Anthropic), and logs whether the current market sentiment is **Bullish**, **Bearish**, or **Mixed**.

Sentiment results are stored in a local `.csv` file with the date, sentiment, model used, model version, article hash, and full raw response — perfect for integrating with trading scripts or position sizing strategies.

## Features

- Pulls the latest article from Schwab's Market Open page
- Supports OpenAI GPT-4 and Anthropic Claude models
- Classifies sentiment as Bullish, Bearish, or Mixed
- Logs results in a `.csv` format with overwrite detection
- Logs full raw LLM response and article content hash for transparency
- Extracts and logs the published date from the article HTML
- Sends push notifications using the Pushover API
- Includes a developer log file with INFO and DEBUG levels
- Controlled via environment variables using `.env`

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a `.env` file

```env
USE_MODEL=anthropic                   # or "openai"
ANTHROPIC_MODEL=claude-opus-4-8
OPENAI_MODEL=gpt-4
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
PUSHOVER_USER_KEY=your-pushover-user-key
PUSHOVER_API_TOKEN=your-pushover-api-token
LOG_LEVEL=INFO                        # or DEBUG, WARNING
```

## Output Example

### Pushover Notification

```
2025-04-11 — Sentiment: Bullish (Model: anthropic / claude-3-5-sonnet-20241022)
```

### CSV Log File (`market_sentiment.csv`)

```csv
publish_date,sentiment,model,model_version,article_hash,raw_response
2025-04-11,Bullish,anthropic,claude-3-5-sonnet-20241022,d41d8cd9,...,"Market sentiment appears bullish based on today's report..."
```

### Debug Log File (`market_sentiment_debug.log`)

```
[INFO] 2025-04-11 08:00:00 — Article content extracted.
[DEBUG] 2025-04-11 08:00:00 — Full article text: ...
```

## Files

- `market_sentiment_checker.py` — Main script
- `.env` — Environment configuration (not committed)
- `market_sentiment.csv` — Main sentiment log
- `market_sentiment_debug.log` — Developer log with INFO and DEBUG messages
- `requirements.txt` — Python dependencies

## Models

| Provider   | Model                             | Use Case                     |
|------------|-----------------------------------|-------------------------------|
| OpenAI     | `gpt-4`                           | Deep analysis                 |
| Anthropic  | `claude-3-5-sonnet-20241022`      | Fast + accurate (latest)     |
| Anthropic  | `claude-3-opus-20240229`          | Most powerful                |
| Anthropic  | `claude-3-sonnet-20240229`        | Balanced performance         |
| Anthropic  | `claude-3-haiku-20240307`         | Fast & lightweight           |

## Notes

- This script is designed for local automation — ideal for use with a cron job.
- The `.env` file allows you to toggle models, enable notifications, and set logging verbosity.
- Ensure `.csv`, `.log`, and `.env` files are listed in `.gitignore`.

## Questions or Contributions?

Feel free to fork the repo, open issues, or share ideas for expanding this project.
