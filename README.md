# hannario-v2

Small Discord companion bot.

## Setup

This project uses `uv` with Python 3.12.

```sh
uv sync
cp .env.example .env
```

Edit `.env` and set `DISCORD_TOKEN`.

In the Discord Developer Portal, enable the bot's **Message Content Intent**.

## Run

```sh
uv run python bot.py
```

## Current behavior

- `!ping` replies with `pong`
- Mentioning the bot replies with a fixed test message
