import argparse
from pathlib import Path
from typing import Any

from show_recent_mentions import read_recent_records


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
    return parser.parse_args()


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
        records = read_recent_records(args.path, args.limit)
    except FileNotFoundError:
        print(f"No observation log found at {args.path}. Run the bot first.")
        return

    if not records:
        print(f"No observation records found in {args.path}.")
        return

    for index, record in enumerate(records):
        if index:
            print()
        print_record(record)


if __name__ == "__main__":
    main()
