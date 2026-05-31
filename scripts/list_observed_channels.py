import argparse
import json
from pathlib import Path
from typing import Any

from show_recent_observations import DEFAULT_OBSERVATION_LOG_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List Discord channels found in the observation log.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_OBSERVATION_LOG_PATH,
        help="Path to the observation JSONL log.",
    )
    return parser.parse_args()


def update_channel_stats(
    stats: dict[str, dict[str, Any]],
    record: dict[str, Any],
) -> None:
    channel_id = str(record.get("channel_id") or "unknown-id")
    timestamp = record.get("timestamp") or "unknown-time"
    item = stats.setdefault(
        channel_id,
        {
            "channel_id": channel_id,
            "channel_name": record.get("channel_name") or "unknown-channel",
            "count": 0,
            "first_observed_at": timestamp,
            "latest_observed_at": timestamp,
            "latest_author": None,
        },
    )

    item["count"] += 1
    item["channel_name"] = record.get("channel_name") or item["channel_name"]
    item["latest_observed_at"] = timestamp
    item["latest_author"] = (
        record.get("author_display_name")
        or record.get("author_id")
        or "unknown-author"
    )


def read_channel_stats(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)

    stats: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        update_channel_stats(stats, json.loads(line))

    return sorted(
        stats.values(),
        key=lambda item: str(item.get("latest_observed_at") or ""),
        reverse=True,
    )


def print_channel(record: dict[str, Any]) -> None:
    name = record.get("channel_name") or "unknown-channel"
    channel_id = record.get("channel_id") or "unknown-id"
    count = record.get("count") or 0
    latest = record.get("latest_observed_at") or "unknown-time"
    latest_author = record.get("latest_author") or "unknown-author"

    print(
        f"#{name} ({channel_id}): "
        f"{count} observations, latest={latest}, latest_author={latest_author}"
    )


def main() -> None:
    args = parse_args()

    try:
        records = read_channel_stats(args.path)
    except FileNotFoundError:
        print(f"No observation log found at {args.path}. Run the bot first.")
        return

    if not records:
        print(f"No observations found in {args.path}.")
        return

    for record in records:
        print_channel(record)


if __name__ == "__main__":
    main()
