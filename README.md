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

## Letta server

Run Letta locally with Docker. The Letta server owns the OpenAI API key; the
Discord bot does not use it directly yet.

```sh
cp .env.letta.example .env.letta
```

Edit `.env.letta` and set `OPENAI_API_KEY`. Do not wrap the value in quotes.

Then start Letta:

```sh
docker compose up -d letta
```

The default local Letta URL is `http://localhost:8283`. Letta's database is
stored in the Docker volume `hannario-v2_letta_pgdata`.

Useful commands:

```sh
docker compose logs -f letta
docker compose down
```

## Letta smoke test

With the Letta server running:

```sh
uv run python scripts/smoke_letta.py
```

The smoke test creates a new throwaway agent and sends one message using:

- `openai/gpt-4o-mini`
- `openai/text-embedding-3-small`

## Create the Discord agent

With the Letta server running:

```sh
uv run python scripts/create_agent.py
```

Copy the printed `LETTA_AGENT_ID=...` line into `.env`.

## Run

Make sure `.env` contains `DISCORD_TOKEN`, `LETTA_BASE_URL`, and
`LETTA_AGENT_ID`.

```sh
uv run python bot.py
```

## Current behavior

- `!ping` replies with `pong`
- Mentioning the bot sends the message to the configured Letta agent
