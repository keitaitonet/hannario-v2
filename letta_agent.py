from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import discord
from letta_client import Letta, MessageCreate, TextContent

from discord_context import format_discord_message


RETURN_MESSAGE_TYPES = [
    "assistant_message",
    "tool_call_message",
    "tool_return_message",
]


@dataclass(frozen=True)
class LettaToolEvent:
    kind: str
    name: str
    arguments: str | None = None
    status: str | None = None
    text: str | None = None


@dataclass(frozen=True)
class LettaReply:
    text: str
    tool_events: list[LettaToolEvent]


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


def read_field(value: Any, field: str) -> Any:
    if isinstance(value, dict):
        return value.get(field)
    return getattr(value, field, None)


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


def extract_tool_events(response: Any) -> list[LettaToolEvent]:
    messages = getattr(response, "messages", None)
    if messages is None and isinstance(response, dict):
        messages = response.get("messages")

    events = []
    for message in messages or []:
        message_type = read_field(message, "message_type")
        if message_type == "tool_call_message":
            tool_calls = read_field(message, "tool_calls") or []
            tool_call = read_field(message, "tool_call")
            if tool_call is not None and not tool_calls:
                tool_calls = [tool_call]

            for call in tool_calls:
                events.append(
                    LettaToolEvent(
                        kind="call",
                        name=str(read_field(call, "name") or "unknown-tool"),
                        arguments=read_field(call, "arguments"),
                    )
                )

        if message_type == "tool_return_message":
            events.append(
                LettaToolEvent(
                    kind="return",
                    name=str(read_field(message, "name") or "unknown-tool"),
                    status=read_field(message, "status"),
                    text=read_field(message, "tool_return"),
                )
            )

    return events


def ask_letta_with_diagnostics(
    client: Letta,
    agent_id: str,
    message: discord.Message,
    bot_user: discord.ClientUser,
    recent_messages: Sequence[discord.Message] | None = None,
    channel_summary: dict[str, Any] | None = None,
) -> LettaReply:
    response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[
            MessageCreate(
                role="user",
                content=[
                    TextContent(
                        text=format_discord_message(
                            message,
                            bot_user,
                            recent_messages,
                            channel_summary,
                        )
                    )
                ],
            )
        ],
        include_return_message_types=RETURN_MESSAGE_TYPES,
    )

    text = extract_assistant_text(response)
    if text is None:
        raise RuntimeError(f"Could not extract assistant text from {type(response)!r}")

    return LettaReply(text=text, tool_events=extract_tool_events(response))


def ask_letta(
    client: Letta,
    agent_id: str,
    message: discord.Message,
    bot_user: discord.ClientUser,
    recent_messages: Sequence[discord.Message] | None = None,
    channel_summary: dict[str, Any] | None = None,
) -> str:
    return ask_letta_with_diagnostics(
        client,
        agent_id,
        message,
        bot_user,
        recent_messages,
        channel_summary,
    ).text
