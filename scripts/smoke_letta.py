import os
from typing import Any

from dotenv import load_dotenv
from letta_client import Letta, MessageCreate, TextContent


DEFAULT_BASE_URL = "http://localhost:8283"
DEFAULT_MODEL = "openai/gpt-4o-mini"
DEFAULT_EMBEDDING = "openai/text-embedding-3-small"


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


def main() -> None:
    load_dotenv()

    client = Letta(base_url=os.getenv("LETTA_BASE_URL", DEFAULT_BASE_URL))
    agent = client.agents.create(
        name=os.getenv("LETTA_AGENT_NAME", "hannario-smoke-test"),
        model=os.getenv("LETTA_MODEL", DEFAULT_MODEL),
        embedding=os.getenv("LETTA_EMBEDDING", DEFAULT_EMBEDDING),
        memory_blocks=[
            {
                "label": "persona",
                "value": "あなたは大学の友達サーバーにいる、落ち着いた日本語の会話相手です。",
            },
            {
                "label": "playbook",
                "value": "短く自然に返す。まだテスト中なので、できることを誇張しない。",
            },
        ],
    )

    print(f"agent_id={agent.id}")

    response = client.agents.messages.create(
        agent_id=agent.id,
        messages=[
            MessageCreate(
                role="user",
                content=[
                    TextContent(text="こんにちは。短く自己紹介して。"),
                ],
            )
        ],
    )

    text = extract_assistant_text(response)
    if text:
        print(text)
    else:
        print(f"Could not extract assistant text from {type(response)!r}.")
        print(response)


if __name__ == "__main__":
    main()
