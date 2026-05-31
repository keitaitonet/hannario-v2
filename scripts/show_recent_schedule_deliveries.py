import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from schedule_runner import DEFAULT_SCHEDULE_LOG_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show recent scheduled Discord task delivery attempts.",
    )
    parser.add_argument("--limit", type=int, default=10, help="Number of records to show.")
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_SCHEDULE_LOG_PATH,
        help="Path to the schedule delivery JSONL log.",
    )
    return parser.parse_args()


def read_recent_records(path: Path, limit: int) -> list[dict[str, Any]]:
    if limit <= 0:
        raise ValueError("limit must be positive.")
    if not path.exists():
        raise FileNotFoundError(path)

    records: deque[dict[str, Any]] = deque(maxlen=limit)
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(json.loads(line))
    return list(records)


def print_record(record: dict[str, Any]) -> None:
    checked_at = record.get("checked_at") or "unknown-time"
    task_id = record.get("task_id") or "-"
    kind = record.get("kind") or "post"
    channel_id = record.get("channel_id") or "-"
    reason = record.get("reason") or "-"
    should_send = record.get("should_send")
    status_after = record.get("status_after") or "-"

    print(f"[{checked_at}] task=#{task_id} kind={kind} channel_id={channel_id}")
    print(f"Send: should_send={should_send} reason={reason} status_after={status_after}")
    message = record.get("message") or ""
    if message:
        print(f"Message: {message}")
    note = record.get("note") or ""
    if note:
        print(f"Note: {note}")
    internal_result = record.get("internal_result") or ""
    if internal_result:
        print(f"Internal result: {internal_result}")


def main() -> None:
    args = parse_args()

    try:
        records = read_recent_records(args.path, args.limit)
    except FileNotFoundError:
        print(f"No schedule delivery log found at {args.path}. Run schedule first.")
        return

    if not records:
        print(f"No schedule delivery records found in {args.path}.")
        return

    for index, record in enumerate(records):
        if index:
            print()
        print_record(record)


if __name__ == "__main__":
    main()
