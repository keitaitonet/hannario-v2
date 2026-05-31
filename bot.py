import logging
import os

import discord
from dotenv import load_dotenv


COMMAND_PREFIX = "!"
MENTION_REPLY = "呼んだ？今は Discord 接続テスト中です。"


def should_ignore_message(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    return message.author == bot_user or message.author.bot


def is_ping_command(message: discord.Message) -> bool:
    return message.content.strip() == f"{COMMAND_PREFIX}ping"


def is_mentioned(message: discord.Message, bot_user: discord.ClientUser) -> bool:
    return bot_user in message.mentions


def build_reply(message: discord.Message, bot_user: discord.ClientUser) -> str | None:
    if is_ping_command(message):
        return "pong"

    if is_mentioned(message, bot_user):
        return MENTION_REPLY

    return None


class HannarioClient(discord.Client):
    async def on_ready(self) -> None:
        if self.user is None:
            return

        logging.info("Logged in as %s (id=%s)", self.user, self.user.id)

    async def on_message(self, message: discord.Message) -> None:
        if self.user is None:
            return

        if should_ignore_message(message, self.user):
            return

        reply = build_reply(message, self.user)
        if reply is None:
            return

        if is_ping_command(message):
            await message.channel.send(reply)
        else:
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

    client = HannarioClient(intents=intents)
    client.run(token, log_handler=None)


if __name__ == "__main__":
    main()
