# Telegram YouTube Inline Bot

A Telegram bot that downloads YouTube videos and serves them via inline mode.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the CDN server (Terminal 1):
```bash
python cdn_server.py
```

3. Start the Telegram bot (Terminal 2):
```bash
python telegram_bot.py
```

## Usage

In any Telegram chat, type:
```
@TWETestBot https://youtube.com/shorts/SF93xtwbS1s?si=4JGD2GmbTxg-wfYj
```

The bot will process the video and show it in inline results. Click to send.

## Important Notes

- Make sure your CDN server is publicly accessible if deploying to production
- Update `CDN_SERVER` in `telegram_bot.py` with your public URL
- Enable inline mode in BotFather for your bot
- Videos are cached in the `downloads/` folder
