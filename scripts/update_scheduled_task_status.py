import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from schedule_db import cancel_scheduled_task, db_path_from_env, mark_scheduled_task_done


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mark a scheduled Discord task done or cancelled.")
    parser.add_argument("task_id", type=int, help="Scheduled task id.")
    status = parser.add_mutually_exclusive_group(required=True)
    status.add_argument("--done", action="store_true", help="Mark the task as done.")
    status.add_argument("--cancel", action="store_true", help="Cancel the task.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=db_path_from_env(),
        help="SQLite database path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.done:
        task = mark_scheduled_task_done(args.task_id, db_path=args.db_path)
    else:
        task = cancel_scheduled_task(args.task_id, db_path=args.db_path)

    if task is None:
        print(f"Task #{args.task_id} was not found.")
        return

    print(f"task #{task.id}: status={task.status}")


if __name__ == "__main__":
    main()
