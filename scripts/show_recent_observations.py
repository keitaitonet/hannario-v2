import argparse
import json
from collections import deque
from pathlib import Path
from typing import Any


DEFAULT_OBSERVATION_LOG_PATH = Path("logs/discord_observations.jsonl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show recent observed non-mention Discord messages.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of recent records to show.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_OBSERVATION_LOG_PATH,
        help="Path to the observation JSONL log.",
    )
    parser.add_argument(
        "--channel",
        help="Only show records from this channel name.",
    )
    parser.add_argument(
        "--channel-id",
        help="Only show records from this Discord channel ID.",
    )
    return parser.parse_args()


def matches_channel_filter(
    record: dict[str, Any],
    channel: str | None,
    channel_id: str | None,
) -> bool:
    if channel is not None and record.get("channel_name") != channel:
        return False
    if channel_id is not None and str(record.get("channel_id")) != channel_id:
        return False
    return True


def read_recent_observation_records(
    path: Path,
    limit: int,
    *,
    channel: str | None = None,
    channel_id: str | None = None,
) -> list[dict[str, Any]]:
    if limit <= 0:
        raise ValueError("limit must be positive.")

    if not path.exists():
        raise FileNotFoundError(path)

    records: deque[dict[str, Any]] = deque(maxlen=limit)
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if matches_channel_filter(record, channel, channel_id):
            records.append(record)

    return list(records)


def print_record(record: dict[str, Any]) -> None:
    timestamp = record.get("timestamp", "unknown-time")
    channel = record.get("channel_name") or record.get("channel_id") or "unknown-channel"
    author = record.get("author_display_name") or record.get("author_id") or "unknown-author"
    user_text = record.get("clean_content") or ""

    print(f"[{timestamp}] #{channel} / {author}")
    print(f"Message: {user_text}")


def main() -> None:
    args = parse_args()

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

    for index, record in enumerate(records):
        if index:
            print()
        print_record(record)


if __name__ == "__main__":
    main()
