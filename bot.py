import asyncio
import logging
import os
from typing import Any

import discord
from dotenv import load_dotenv
from letta_client import Letta, MessageCreate, TextContent


COMMAND_PREFIX = "!"
DEFAULT_LETTA_BASE_URL = "http://localhost:8283"
LETTA_ERROR_REPLY = "ごめん、今ちょっと考える側につながらない。"


def should_ignore_message(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    return message.author == bot_user or message.author.bot


def is_ping_command(message: discord.Message) -> bool:
    return message.content.strip() == f"{COMMAND_PREFIX}ping"


def is_mentioned(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    return bot_user in message.mentions


def read_text(value: Any) -> str | None:
    if isinstance(value, str):
        return value

    if isinstance(value, list):
        parts = [read_text(item) for item in value]
        text = "\n".join(part for part in parts if part)
        return text or None

    if isinstance(value, dict):
        for key in ("text", "content", "message"):
            text = read_text(value.get(key))
            if text:
                return text

    for attr in ("text", "content", "message"):
        if hasattr(value, attr):
            text = read_text(getattr(value, attr))
            if text:
                return text

    return None


def extract_assistant_text(response: Any) -> str | None:
    messages = getattr(response, "messages", None)
    if messages is None and isinstance(response, dict):
        messages = response.get("messages")

    if not messages:
        return read_text(response)

    for message in reversed(messages):
        role = getattr(message, "role", None)
        message_type = getattr(message, "message_type", None)
        if isinstance(message, dict):
            role = message.get("role")
            message_type = message.get("message_type")

        if role == "assistant" or message_type == "assistant_message":
            text = read_text(message)
            if text:
                return text

    return None


def format_discord_message(message: discord.Message) -> str:
    channel_name = getattr(message.channel, "name", "direct-message")
    return (
        "Discord message\n"
        f"author: {message.author.display_name}\n"
        f"channel: {channel_name}\n"
        f"content: {message.content}"
    )


def ask_letta(client: Letta, agent_id: str, message: discord.Message) -> str:
    response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[
            MessageCreate(
                role="user",
                content=[TextContent(text=format_discord_message(message))],
            )
        ],
    )

    text = extract_assistant_text(response)
    if text is None:
        raise RuntimeError(f"Could not extract assistant text from {type(response)!r}")

    return text


class HannarioClient(discord.Client):
    def __init__(self, *, letta_client: Letta, letta_agent_id: str | None, **kwargs: Any):
        super().__init__(**kwargs)
        self.letta_client = letta_client
        self.letta_agent_id = letta_agent_id

    async def on_ready(self) -> None:
        if self.user is None:
            return

        logging.info("Logged in as %s (id=%s)", self.user, self.user.id)

    async def on_message(self, message: discord.Message) -> None:
        if self.user is None:
            return

        if should_ignore_message(message, self.user):
            return

        if is_ping_command(message):
            await message.channel.send("pong")
            return

        if not is_mentioned(message, self.user):
            return

        if self.letta_agent_id is None:
            await message.reply("LETTA_AGENT_ID がまだ設定されていません。", mention_author=False)
            return

        async with message.channel.typing():
            try:
                reply = await asyncio.wait_for(
                    asyncio.to_thread(
                        ask_letta,
                        self.letta_client,
                        self.letta_agent_id,
                        message,
                    ),
                    timeout=45,
                )
            except Exception:
                logging.exception("Failed to get Letta reply")
                reply = LETTA_ERROR_REPLY

        await message.reply(reply, mention_author=False)


def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit("Missing DISCORD_TOKEN. Create .env from .env.example.")

    intents = discord.Intents.default()
    intents.message_content = True

    letta_client = Letta(base_url=os.getenv("LETTA_BASE_URL", DEFAULT_LETTA_BASE_URL))
    letta_agent_id = os.getenv("LETTA_AGENT_ID")

    client = HannarioClient(
        intents=intents,
        letta_client=letta_client,
        letta_agent_id=letta_agent_id,
    )
    client.run(token, log_handler=None)


if __name__ == "__main__":
    main()
