import argparse
from pathlib import Path
from typing import Any

from show_channel_context import format_channel_context
from show_recent_mentions import DEFAULT_LOG_PATH, read_recent_records
from show_recent_observations import (
    DEFAULT_OBSERVATION_LOG_PATH,
    read_recent_observation_records,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Discord API recent context saved on a mention with "
            "observation-log context from the same channel."
        ),
    )
    parser.add_argument(
        "--mention-path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Path to the mention JSONL log.",
    )
    parser.add_argument(
        "--observation-path",
        type=Path,
        default=DEFAULT_OBSERVATION_LOG_PATH,
        help="Path to the observation JSONL log.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of observed same-channel records to show.",
    )
    return parser.parse_args()


def format_saved_recent_context(record: dict[str, Any]) -> str:
    channel_name = record.get("channel_name") or "unknown-channel"
    channel_id = record.get("channel_id") or "unknown-id"
    lines = [
        "saved_discord_api_recent_context_oldest_first:",
        f"channel: {channel_name} ({channel_id})",
    ]

    for item in record.get("recent_context") or []:
        timestamp = item.get("timestamp", "unknown-time")
        author = (
            item.get("author_display_name")
            or item.get("author_id")
            or "unknown-author"
        )
        author_id = item.get("author_id") or "unknown-id"
        text = item.get("clean_content") or ""
        lines.append(f"- {timestamp} {author} ({author_id}): {text}")

    return "\n".join(lines)


def format_current_mention(record: dict[str, Any]) -> str:
    timestamp = record.get("timestamp", "unknown-time")
    author = (
        record.get("author_display_name")
        or record.get("author_id")
        or "unknown-author"
    )
    author_id = record.get("author_id") or "unknown-id"
    user_text = record.get("clean_content") or ""
    bot_reply = record.get("bot_reply") or ""
    return "\n".join(
        [
            "mention:",
            f"- {timestamp} {author} ({author_id}): {user_text}",
            f"bot_reply: {bot_reply}",
        ]
    )


def main() -> None:
    args = parse_args()

    try:
        mention_records = read_recent_records(args.mention_path, 1)
    except FileNotFoundError:
        print(f"No mention log found at {args.mention_path}. Run the bot and mention it first.")
        return

    if not mention_records:
        print(f"No mention records found in {args.mention_path}.")
        return

    mention = mention_records[-1]
    channel_id = mention.get("channel_id")
    channel_name = mention.get("channel_name")

    try:
        observed_records = read_recent_observation_records(
            args.observation_path,
            args.limit,
            channel_id=str(channel_id) if channel_id is not None else None,
        )
    except FileNotFoundError:
        observed_records = []

    print(format_current_mention(mention))
    print()
    print(format_saved_recent_context(mention))
    print()
    if observed_records:
        print(
            format_channel_context(
                observed_records,
                channel=channel_name,
                channel_id=str(channel_id) if channel_id is not None else None,
            )
        )
    else:
        print("observed_same_channel_context_oldest_first:")
        print(f"channel: {channel_name or channel_id or 'unknown-channel'}")
        print("(no observed records)")


if __name__ == "__main__":
    main()
