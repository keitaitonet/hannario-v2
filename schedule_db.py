import os
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast


DEFAULT_DB_PATH = Path("data/local.sqlite3")
SCHEDULE_STATUS_PENDING = "pending"
SCHEDULE_STATUS_DONE = "done"
SCHEDULE_STATUS_CANCELLED = "cancelled"
SCHEDULE_KIND_POST = "post"
SCHEDULE_KIND_THINK = "think"
SCHEDULE_KIND_OBSERVE = "observe"
SCHEDULE_KIND_FOLLOW_UP = "follow_up"
ScheduleStatus = Literal["pending", "done", "cancelled"]
ScheduleKind = Literal["post", "think", "observe", "follow_up"]
VALID_SCHEDULE_KINDS = {
    SCHEDULE_KIND_POST,
    SCHEDULE_KIND_THINK,
    SCHEDULE_KIND_OBSERVE,
    SCHEDULE_KIND_FOLLOW_UP,
}


@dataclass(frozen=True)
class ScheduledTask:
    id: int
    channel_id: str
    message: str
    due_at: str
    status: ScheduleStatus
    kind: ScheduleKind
    created_at: str
    note: str | None = None
    created_by: str | None = None
    source_message_id: str | None = None
    completed_at: str | None = None
    cancelled_at: str | None = None


def db_path_from_env() -> Path:
    raw_value = os.getenv("HANNARIO_DB_PATH")
    if raw_value is None or not raw_value.strip():
        return DEFAULT_DB_PATH
    return Path(raw_value)


def utc_isoformat(value: datetime | None = None) -> str:
    actual_value = value or datetime.now(UTC)
    if actual_value.tzinfo is None:
        actual_value = actual_value.replace(tzinfo=UTC)
    return actual_value.astimezone(UTC).isoformat()


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or db_path_from_env()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Path | None = None) -> None:
    with connect(db_path) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                message TEXT NOT NULL,
                due_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'done', 'cancelled')),
                kind TEXT NOT NULL DEFAULT 'post',
                created_at TEXT NOT NULL,
                note TEXT,
                created_by TEXT,
                source_message_id TEXT,
                completed_at TEXT,
                cancelled_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_due_pending
            ON scheduled_tasks (status, due_at)
            """
        )
        column_names = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(scheduled_tasks)").fetchall()
        }
        if "kind" not in column_names:
            connection.execute(
                "ALTER TABLE scheduled_tasks ADD COLUMN kind TEXT NOT NULL DEFAULT 'post'"
            )
        if "note" not in column_names:
            connection.execute("ALTER TABLE scheduled_tasks ADD COLUMN note TEXT")


def row_to_scheduled_task(row: sqlite3.Row) -> ScheduledTask:
    return ScheduledTask(
        id=int(row["id"]),
        channel_id=str(row["channel_id"]),
        message=str(row["message"]),
        due_at=str(row["due_at"]),
        status=cast(ScheduleStatus, str(row["status"])),
        kind=cast(ScheduleKind, str(row["kind"])),
        created_at=str(row["created_at"]),
        note=row["note"],
        created_by=row["created_by"],
        source_message_id=row["source_message_id"],
        completed_at=row["completed_at"],
        cancelled_at=row["cancelled_at"],
    )


def create_scheduled_task(
    *,
    channel_id: str,
    message: str,
    due_at: datetime,
    kind: ScheduleKind = SCHEDULE_KIND_POST,
    note: str | None = None,
    created_by: str | None = None,
    source_message_id: str | None = None,
    db_path: Path | None = None,
    now: datetime | None = None,
) -> ScheduledTask:
    if not channel_id.strip():
        raise ValueError("channel_id must not be empty.")
    if not message.strip():
        raise ValueError("message must not be empty.")
    if kind not in VALID_SCHEDULE_KINDS:
        raise ValueError(f"kind must be one of {sorted(VALID_SCHEDULE_KINDS)}.")

    initialize_database(db_path)
    with connect(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO scheduled_tasks (
                channel_id,
                message,
                due_at,
                status,
                kind,
                created_at,
                note,
                created_by,
                source_message_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                channel_id,
                message,
                utc_isoformat(due_at),
                SCHEDULE_STATUS_PENDING,
                kind,
                utc_isoformat(now),
                note,
                created_by,
                source_message_id,
            ),
        )
        task_id = int(cursor.lastrowid)

    task = get_scheduled_task(task_id, db_path=db_path)
    if task is None:
        raise RuntimeError(f"Created scheduled task {task_id}, but it could not be read back.")
    return task


def get_scheduled_task(task_id: int, *, db_path: Path | None = None) -> ScheduledTask | None:
    initialize_database(db_path)
    with connect(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM scheduled_tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        return None
    return row_to_scheduled_task(row)


def list_scheduled_tasks(
    *,
    db_path: Path | None = None,
    status: ScheduleStatus | Literal["all"] = SCHEDULE_STATUS_PENDING,
    limit: int = 50,
) -> list[ScheduledTask]:
    if limit <= 0:
        raise ValueError("limit must be positive.")

    initialize_database(db_path)
    with connect(db_path) as connection:
        if status == "all":
            rows = connection.execute(
                "SELECT * FROM scheduled_tasks ORDER BY due_at ASC, id ASC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT * FROM scheduled_tasks
                WHERE status = ?
                ORDER BY due_at ASC, id ASC
                LIMIT ?
                """,
                (status, limit),
            ).fetchall()

    return [row_to_scheduled_task(row) for row in rows]


def list_due_scheduled_tasks(
    *,
    db_path: Path | None = None,
    now: datetime | None = None,
    limit: int = 10,
    kind: ScheduleKind = SCHEDULE_KIND_POST,
) -> list[ScheduledTask]:
    if limit <= 0:
        raise ValueError("limit must be positive.")

    if kind not in VALID_SCHEDULE_KINDS:
        raise ValueError(f"kind must be one of {sorted(VALID_SCHEDULE_KINDS)}.")

    initialize_database(db_path)
    due_at_or_before = utc_isoformat(now)
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT * FROM scheduled_tasks
            WHERE status = ? AND due_at <= ? AND kind = ?
            ORDER BY due_at ASC, id ASC
            LIMIT ?
            """,
            (SCHEDULE_STATUS_PENDING, due_at_or_before, kind, limit),
        ).fetchall()

    return [row_to_scheduled_task(row) for row in rows]


def mark_scheduled_task_done(
    task_id: int,
    *,
    db_path: Path | None = None,
    now: datetime | None = None,
) -> ScheduledTask | None:
    initialize_database(db_path)
    with connect(db_path) as connection:
        connection.execute(
            """
            UPDATE scheduled_tasks
            SET status = ?, completed_at = ?, cancelled_at = NULL
            WHERE id = ? AND status = ?
            """,
            (
                SCHEDULE_STATUS_DONE,
                utc_isoformat(now),
                task_id,
                SCHEDULE_STATUS_PENDING,
            ),
        )

    return get_scheduled_task(task_id, db_path=db_path)


def cancel_scheduled_task(
    task_id: int,
    *,
    db_path: Path | None = None,
    now: datetime | None = None,
) -> ScheduledTask | None:
    initialize_database(db_path)
    with connect(db_path) as connection:
        connection.execute(
            """
            UPDATE scheduled_tasks
            SET status = ?, cancelled_at = ?, completed_at = NULL
            WHERE id = ? AND status = ?
            """,
            (
                SCHEDULE_STATUS_CANCELLED,
                utc_isoformat(now),
                task_id,
                SCHEDULE_STATUS_PENDING,
            ),
        )

    return get_scheduled_task(task_id, db_path=db_path)
