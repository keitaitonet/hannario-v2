import argparse
import json
from collections import deque
from pathlib import Path
from typing import Any

from show_recent_observations import matches_channel_filter
from summarize_channel_observations import DEFAULT_SUMMARY_LOG_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show saved Discord channel observation summaries.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of recent summaries to show.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_SUMMARY_LOG_PATH,
        help="Path to the channel summary JSONL log.",
    )
    parser.add_argument(
        "--channel",
        help="Only show summaries from this channel name.",
    )
    parser.add_argument(
        "--channel-id",
        help="Only show summaries from this Discord channel ID.",
    )
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Also print the summarized input context.",
    )
    return parser.parse_args()


def read_recent_summary_records(
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


def print_record(record: dict[str, Any], *, show_context: bool = False) -> None:
    created_at = record.get("created_at", "unknown-time")
    channel = record.get("channel_name") or record.get("channel_id") or "unknown-channel"
    record_count = record.get("record_count", "?")
    first_observed_at = record.get("first_observed_at") or "unknown-start"
    last_observed_at = record.get("last_observed_at") or "unknown-end"
    model = record.get("model") or "unknown-model"
    summary = record.get("summary") or ""

    print(f"[{created_at}] #{channel} / {record_count} records / {model}")
    print(f"Range: {first_observed_at} -> {last_observed_at}")
    print("Summary:")
    print(summary)
    if show_context:
        print("Context:")
        print(record.get("context") or "")


def main() -> None:
    args = parse_args()

    try:
        records = read_recent_summary_records(
            args.path,
            args.limit,
            channel=args.channel,
            channel_id=args.channel_id,
        )
    except FileNotFoundError:
        print(f"No channel summary log found at {args.path}. Run a summary with --save first.")
        return

    if not records:
        print(f"No matching channel summaries found in {args.path}.")
        return

    for index, record in enumerate(records):
        if index:
            print()
        print_record(record, show_context=args.show_context)


if __name__ == "__main__":
    main()
