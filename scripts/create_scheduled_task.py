import argparse
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from schedule_db import (
    SCHEDULE_KIND_FOLLOW_UP,
    SCHEDULE_KIND_OBSERVE,
    SCHEDULE_KIND_POST,
    SCHEDULE_KIND_THINK,
    create_scheduled_task,
    db_path_from_env,
)


DEFAULT_TIMEZONE = "Asia/Tokyo"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a scheduled Discord task.")
    parser.add_argument("--channel-id", required=True, help="Discord channel id to post to.")
    parser.add_argument("--message", required=True, help="Message to post when due.")
    parser.add_argument(
        "--due-at",
        required=True,
        help="ISO timestamp. Naive values are interpreted in --timezone.",
    )
    parser.add_argument(
        "--timezone",
        default=DEFAULT_TIMEZONE,
        help=f"Timezone for naive --due-at values. Default: {DEFAULT_TIMEZONE}",
    )
    parser.add_argument("--created-by", help="Optional creator user id or name.")
    parser.add_argument("--source-message-id", help="Optional Discord source message id.")
    parser.add_argument(
        "--kind",
        choices=[
            SCHEDULE_KIND_POST,
            SCHEDULE_KIND_THINK,
            SCHEDULE_KIND_OBSERVE,
            SCHEDULE_KIND_FOLLOW_UP,
        ],
        default=SCHEDULE_KIND_POST,
        help="Schedule kind. post sends to Discord; other kinds are internal for now.",
    )
    parser.add_argument("--note", help="Optional internal note for this scheduled task.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=db_path_from_env(),
        help="SQLite database path.",
    )
    return parser.parse_args()


def parse_due_at(value: str, timezone_name: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is not None:
        return parsed
    return parsed.replace(tzinfo=ZoneInfo(timezone_name))


def main() -> None:
    args = parse_args()
    task = create_scheduled_task(
        channel_id=args.channel_id,
        message=args.message,
        due_at=parse_due_at(args.due_at, args.timezone),
        kind=args.kind,
        note=args.note,
        created_by=args.created_by,
        source_message_id=args.source_message_id,
        db_path=args.db_path,
    )
    print(
        f"created task #{task.id}: status={task.status} "
        f"kind={task.kind} channel_id={task.channel_id} due_at={task.due_at}"
    )
    print(f"message: {task.message}")
    if task.note:
        print(f"note: {task.note}")


if __name__ == "__main__":
    main()
