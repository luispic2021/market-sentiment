# market-sentiment-check.py
#
# This script is designed to fetch the latest market sentiment article, analyze its sentiment,
# and log the results. It also sends a push notification with the sentiment analysis.
# Ensure you have the required packages installed:
# pip install requests beautifulsoup4 python-dotenv openai anthropic
# Make sure to set the environment variables in a .env file or your system environment.
# The script will log messages based on the configured log level and send notifications via Pushover.
# The script will retry fetching the article if it has not been updated today.
# It will also handle errors gracefully and log them accordingly.
# Note: The script assumes the article structure remains consistent with the current implementation.
# Ensure you have the necessary permissions and API keys set up for OpenAI or Anthropic.
# The script is designed to run periodically, so consider using a task scheduler like cron or Windows Task Scheduler.
# Make sure to test the script in a controlled environment before deploying it in production.
# The script is intended for educational purposes and should be used responsibly.

import os
import requests
import hashlib
import csv
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USE_MODEL = os.getenv("USE_MODEL", "openai")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-8")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

if USE_MODEL == "openai" and OPENAI_API_KEY:
    import openai
    openai.api_key = OPENAI_API_KEY
elif USE_MODEL == "anthropic" and ANTHROPIC_API_KEY:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    raise ValueError("Missing or invalid API configuration.")

def log_message(level, message, debug_file="market_sentiment_debug.log"):
    levels = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
    current_level = levels.get(LOG_LEVEL.upper(), 20)
    message_level = levels.get(level.upper(), 100)
    if message_level >= current_level:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(debug_file, "a") as log:
            log.write(f"[{level.upper()}] {timestamp} — {message}\n")

def send_push_notification(message):
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        log_message("WARNING", "Pushover credentials not found. Skipping notification.")
        return

    payload = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": message
    }
    response = requests.post("https://api.pushover.net/1/messages.json", data=payload)
    if response.status_code != 200:
        log_message("WARNING", f"Pushover notification failed: {response.text}")
    else:
        log_message("INFO", "Push notification sent successfully.")

def fetch_article():
    url = "https://www.schwab.com/learn/story/stock-market-update-open"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    # Save response to a file for debugging
    with open("article_html.log", "w", encoding="utf-8") as f:
        f.write(response.text)
    return response.text

def extract_article_text(html):
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find_all("p")
    article_text = "\n".join(p.get_text() for p in paragraphs if p.get_text().strip())
    # Save response to a file for debugging
    with open("article.log", "w", encoding="utf-8") as f:
        f.write(article_text)
    return article_text

def extract_publish_datetime(html):
    soup = BeautifulSoup(html, "html.parser")
    match = soup.find(string=re.compile("Published as of:"))
    if match:
        # Step 1: Extract resilient short date for comparison (e.g., 'April 17, 2025')
        short_date_match = re.search(r"Published as of: ([A-Za-z]+ \d{1,2}, \d{4})", match)
        # Step 2: Extract full raw date string for push notification (e.g., 'April 17, 2025, 9:15 a.m. ET')
        full_date_match = re.search(r"Published as of: (.+)", match)
        log_message("DEBUG", f"Extracted full date text: {full_date_match.group(1) if full_date_match else 'None'}")
        if short_date_match and full_date_match:
            try:
                short_clean_str = short_date_match.group(1).strip()
                short_dt = datetime.strptime(short_clean_str, "%B %d, %Y")
                log_message("DEBUG", f"Parsed short date: {short_dt}")
                return short_dt.strftime("%Y-%m-%d"), full_date_match.group(1)
            except ValueError as e:
                log_message("ERROR", f"Failed parsing short datetime: {e}")
    raise ValueError("Could not extract publish date from article.")

def get_article_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

def get_sentiment(article):
    prompt = f"""
You are a financial analyst. Based on the following article, determine whether the market sentiment for today is bullish, bearish, or mixed.
Respond with only one word: Bullish, Bearish, or Mixed at the start,  followed by 2-3 key indicators that explain your reasoning.

Article:
{article[:3000]}
"""
    if USE_MODEL == "openai":
        completion = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip(), OPENAI_MODEL
    elif USE_MODEL == "anthropic":
        request = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}],
        }
        if not ANTHROPIC_MODEL.startswith("claude-opus-4-7") and not ANTHROPIC_MODEL.startswith("claude-opus-4-8"):
            request["temperature"] = 0
        response = client.messages.create(**request)
        return response.content[0].text.strip(), ANTHROPIC_MODEL
    return "Undetermined", "unknown"

def clean_sentiment(raw):
    first_word = raw.strip().split()[0].lower().rstrip(".")
    return first_word.capitalize() if first_word in {"bullish", "bearish", "mixed"} else "Undetermined"

def write_log_csv(today, raw_publish, sentiment, model_used, model_version, article_hash, raw_response, filename="market_sentiment.csv"):
    file_exists = os.path.isfile(filename)
    rows = []

    if file_exists:
        with open(filename, mode="r", newline="") as file:
            rows = list(csv.reader(file))

    header = ["today_date", "raw_publish_date", "sentiment", "model", "model_version", "article_hash", "raw_response"]
    log_row = [today, raw_publish, sentiment, model_used, model_version, article_hash, raw_response]
    updated = False

    for i, row in enumerate(rows):
        if row and row[0] == today:
            rows[i] = log_row
            updated = True
            break

    if not updated:
        if not rows:
            rows.append(header)
        rows.append(log_row)

    with open(filename, mode="w", newline="") as file:
        csv.writer(file).writerows(rows)

def main(retry=False):
    html = fetch_article()
    article = extract_article_text(html)
    log_message("INFO", "Fetched article text successfully. Check article.log for details.")
    try:
        publish_date, raw_publish_str = extract_publish_datetime(html)
    except ValueError as e:
        log_message("WARNING", f"{e}. Retrying in 10 seconds...")
        if not retry:
            time.sleep(10)
            return main(retry=True)
        else:
            log_message("ERROR", "Retry failed. Still unable to extract publish date.")
            return
    log_message("INFO", f"Fetched article published on: {raw_publish_str}")

    today_str = datetime.now().strftime("%Y-%m-%d")

    if today_str != publish_date:
        msg = f"Article has not been updated today. Publish time: {raw_publish_str}"
        log_message("INFO", msg)
        if not retry:
            log_message("INFO", "Retrying in 1 minute...")
            time.sleep(300)
            return main(retry=True)
        else:
            log_message("WARNING", "Retry failed, article still not updated.")
            return

    sentiment_raw, model_version = get_sentiment(article)

    sentiment = clean_sentiment(sentiment_raw)
    article_hash = get_article_hash(article)
    write_log_csv(today_str, raw_publish_str, sentiment, USE_MODEL, model_version, article_hash, sentiment_raw)
    log_message("INFO", f"Sentiment for {today_str}: {sentiment}")
    log_message("DEBUG", f"Article hash: {article_hash}")
    log_message("DEBUG", f"Raw response: {sentiment_raw}")
    log_message("INFO", "Logging complete. Sending push notification...")

    push_message = f"{raw_publish_str} — Sentiment: {sentiment_raw[:400]}\nModel: {model_version}"
    send_push_notification(push_message)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_message("ERROR", f"Unhandled failure: {type(e).__name__}: {e}")
        raise
