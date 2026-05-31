import logging
import os

import discord
from dotenv import load_dotenv


COMMAND_PREFIX = "!"


class HannarioClient(discord.Client):
    async def on_ready(self) -> None:
        if self.user is None:
            return

        logging.info("Logged in as %s (id=%s)", self.user, self.user.id)

    async def on_message(self, message: discord.Message) -> None:
        if self.user is None:
            return

        if message.author == self.user or message.author.bot:
            return

        content = message.content.strip()

        if content == f"{COMMAND_PREFIX}ping":
            await message.channel.send("pong")
            return

        if self.user in message.mentions:
            await message.reply(
                "呼んだ？今は Discord 接続テスト中です。",
                mention_author=False,
            )


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
