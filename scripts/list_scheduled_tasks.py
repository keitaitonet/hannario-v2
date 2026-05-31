import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from schedule_db import db_path_from_env, list_due_scheduled_tasks, list_scheduled_tasks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List scheduled Discord tasks.")
    parser.add_argument(
        "--status",
        choices=["pending", "done", "cancelled", "all"],
        default="pending",
        help="Task status to show.",
    )
    parser.add_argument(
        "--due",
        action="store_true",
        help="Show pending tasks that are due now.",
    )
    parser.add_argument("--limit", type=int, default=20, help="Maximum tasks to show.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=db_path_from_env(),
        help="SQLite database path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.due:
        tasks = list_due_scheduled_tasks(db_path=args.db_path, limit=args.limit)
    else:
        tasks = list_scheduled_tasks(
            db_path=args.db_path,
            status=args.status,  # type: ignore[arg-type]
            limit=args.limit,
        )

    if not tasks:
        print("No scheduled tasks found.")
        return

    for task in tasks:
        print(f"#{task.id} [{task.status}] due_at={task.due_at} channel_id={task.channel_id}")
        print(f"message: {task.message}")
        if task.created_by:
            print(f"created_by: {task.created_by}")
        if task.source_message_id:
            print(f"source_message_id: {task.source_message_id}")
        if task.completed_at:
            print(f"completed_at: {task.completed_at}")
        if task.cancelled_at:
            print(f"cancelled_at: {task.cancelled_at}")
        print()


if __name__ == "__main__":
    main()
