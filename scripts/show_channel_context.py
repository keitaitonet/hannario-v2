import argparse
from pathlib import Path
from typing import Any

from show_recent_observations import (
    DEFAULT_OBSERVATION_LOG_PATH,
    read_recent_observation_records,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show recent observed context for one Discord channel.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of recent channel records to show.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_OBSERVATION_LOG_PATH,
        help="Path to the observation JSONL log.",
    )
    parser.add_argument(
        "--channel",
        help="Show records from this channel name.",
    )
    parser.add_argument(
        "--channel-id",
        help="Show records from this Discord channel ID.",
    )
    return parser.parse_args()


def require_channel_filter(channel: str | None, channel_id: str | None) -> None:
    if channel is None and channel_id is None:
        raise SystemExit("Specify --channel or --channel-id.")


def channel_label(
    records: list[dict[str, Any]],
    channel: str | None,
    channel_id: str | None,
) -> str:
    if records:
        record = records[-1]
        name = record.get("channel_name") or channel or "unknown-channel"
        identifier = record.get("channel_id") or channel_id or "unknown-id"
        return f"{name} ({identifier})"
    if channel is not None and channel_id is not None:
        return f"{channel} ({channel_id})"
    return channel or channel_id or "unknown-channel"


def format_channel_context(
    records: list[dict[str, Any]],
    *,
    channel: str | None = None,
    channel_id: str | None = None,
) -> str:
    lines = [
        "observed_same_channel_context_oldest_first:",
        f"channel: {channel_label(records, channel, channel_id)}",
    ]

    for record in records:
        timestamp = record.get("timestamp", "unknown-time")
        author = (
            record.get("author_display_name")
            or record.get("author_id")
            or "unknown-author"
        )
        author_id = record.get("author_id") or "unknown-id"
        text = record.get("clean_content") or ""
        lines.append(f"- {timestamp} {author} ({author_id}): {text}")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    require_channel_filter(args.channel, args.channel_id)

    try:
        records = read_recent_observation_records(
            args.path,
            args.limit,
            channel=args.channel,
            channel_id=args.channel_id,
        )
    except FileNotFoundError:
        print(f"No observation log found at {args.path}. Run the bot first.")
        return

    if not records:
        print(f"No matching observation records found in {args.path}.")
        return

    print(format_channel_context(records, channel=args.channel, channel_id=args.channel_id))


if __name__ == "__main__":
    main()
