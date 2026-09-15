# Price Watcher

A price-tracking bot that checks a list of product pages on a schedule and sends a Discord notification when the price drops to or below a target you set.

## How it works

- Each tracked product lives in `config.json`, with a URL, a target price, and a scraping strategy.
- `scraper.py` fetches each product page and extracts the current price from the page's JSON-LD structured data (`<script type="application/ld+json">`).
- `storage.json` remembers the last known price and whether a notification has already been sent for the current dip, so you only get notified once per sale — not on every check while the price stays low.
- `notifier.py` sends a message to a Discord channel via a webhook when a price crosses below its target.
- `main.py` ties it all together: load config, check each product, compare against target, notify if needed, save updated state.
- A GitHub Actions workflow (`.github/workflows/price-check.yml`) runs the checker on a schedule (roughly every hour) so it works without your computer needing to be on.

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you don't have it:
   ```bash
   brew install uv
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Create a Discord webhook: in your server, go to a channel's settings → Integrations → Webhooks → New Webhook, then copy the URL.

4. Create a `.env` file in the project root:
   ```
   DISCORD_WEBHOOK_URL=your_webhook_url_here
   ```

5. Add products to track in `config.json`:
   ```json
   [
     {
       "id": "unique-product-id",
       "name": "Product Name",
       "url": "https://example.com/product",
       "target_price": 49.99,
       "strategy": "json-ld",
       "selector": null
     }
   ]
   ```

## Running locally

```bash
uv run python -m price_watcher.main
```

## Running on a schedule (GitHub Actions)

The included workflow runs the checker automatically once an hour, even when your machine is off.

To set it up:

1. Push this repo to GitHub.
2. Go to **Settings → Secrets and variables → Actions** and add a repository secret named `DISCORD_WEBHOOK_URL` with your webhook URL.
3. Make sure **Settings → Actions → General → Workflow permissions** is set to "Read and write permissions" — the workflow commits the updated `storage.json` back to the repo after each run.
4. Trigger a manual run from the **Actions** tab ("Run workflow") to confirm it works, then let the schedule take over.


## Notification behavior

- A notification is sent the first time a product's price drops to or below its `target_price`.
- No further notifications are sent while the price stays at or below target.
- If the price rises back above target and later drops again, you'll be notified again — one alert per sale event.
