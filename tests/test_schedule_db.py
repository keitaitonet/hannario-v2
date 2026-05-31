import os
import sqlite3
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from schedule_db import (
    DEFAULT_DB_PATH,
    SCHEDULE_KIND_POST,
    SCHEDULE_KIND_THINK,
    SCHEDULE_STATUS_CANCELLED,
    SCHEDULE_STATUS_DONE,
    SCHEDULE_STATUS_PENDING,
    cancel_scheduled_task,
    create_scheduled_task,
    db_path_from_env,
    initialize_database,
    list_due_scheduled_tasks,
    list_scheduled_tasks,
    mark_scheduled_task_done,
    utc_isoformat,
)


class ScheduleDbTest(unittest.TestCase):
    def test_db_path_from_env_defaults_to_local_sqlite(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(db_path_from_env(), DEFAULT_DB_PATH)

    def test_db_path_from_env_uses_override(self) -> None:
        with patch.dict(os.environ, {"HANNARIO_DB_PATH": "data/test.sqlite3"}):
            self.assertEqual(db_path_from_env(), Path("data/test.sqlite3"))

    def test_initialize_database_creates_parent_and_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "nested" / "local.sqlite3"

            initialize_database(db_path)

            self.assertTrue(db_path.exists())

    def test_create_and_list_scheduled_task(self) -> None:
        due_at = datetime(2026, 6, 1, 12, 0, tzinfo=UTC)
        created_at = datetime(2026, 6, 1, 11, 0, tzinfo=UTC)

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "local.sqlite3"

            task = create_scheduled_task(
                channel_id="1421460487639535667",
                message="昼です",
                due_at=due_at,
                kind=SCHEDULE_KIND_THINK,
                note="未来の自分へのメモ",
                created_by="user-1",
                source_message_id="message-1",
                db_path=db_path,
                now=created_at,
            )
            tasks = list_scheduled_tasks(db_path=db_path)

        self.assertEqual(task.id, 1)
        self.assertEqual(task.status, SCHEDULE_STATUS_PENDING)
        self.assertEqual(task.kind, SCHEDULE_KIND_THINK)
        self.assertEqual(task.note, "未来の自分へのメモ")
        self.assertEqual(task.due_at, "2026-06-01T12:00:00+00:00")
        self.assertEqual(task.created_at, "2026-06-01T11:00:00+00:00")
        self.assertEqual(task.created_by, "user-1")
        self.assertEqual(task.source_message_id, "message-1")
        self.assertEqual(tasks, [task])

    def test_create_rejects_empty_fields(self) -> None:
        due_at = datetime(2026, 6, 1, 12, 0, tzinfo=UTC)
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "local.sqlite3"

            with self.assertRaises(ValueError):
                create_scheduled_task(
                    channel_id="",
                    message="hello",
                    due_at=due_at,
                    db_path=db_path,
                )
            with self.assertRaises(ValueError):
                create_scheduled_task(
                    channel_id="123",
                    message="",
                    due_at=due_at,
                    db_path=db_path,
                )
            with self.assertRaises(ValueError):
                create_scheduled_task(
                    channel_id="123",
                    message="hello",
                    due_at=due_at,
                    kind="bad",  # type: ignore[arg-type]
                    db_path=db_path,
                )

    def test_list_due_scheduled_tasks_returns_only_due_pending_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "local.sqlite3"
            create_scheduled_task(
                channel_id="123",
                message="past",
                due_at=datetime(2026, 6, 1, 9, 0, tzinfo=UTC),
                db_path=db_path,
            )
            create_scheduled_task(
                channel_id="123",
                message="think",
                due_at=datetime(2026, 6, 1, 9, 0, tzinfo=UTC),
                kind=SCHEDULE_KIND_THINK,
                db_path=db_path,
            )
            future_task = create_scheduled_task(
                channel_id="123",
                message="future",
                due_at=datetime(2026, 6, 1, 11, 0, tzinfo=UTC),
                db_path=db_path,
            )
            mark_scheduled_task_done(future_task.id, db_path=db_path)

            due_tasks = list_due_scheduled_tasks(
                db_path=db_path,
                now=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
            )

        self.assertEqual([task.message for task in due_tasks], ["past"])

    def test_initialize_database_migrates_existing_table(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "local.sqlite3"

            with sqlite3.connect(db_path) as connection:
                connection.execute(
                    """
                    CREATE TABLE scheduled_tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        channel_id TEXT NOT NULL,
                        message TEXT NOT NULL,
                        due_at TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        created_at TEXT NOT NULL,
                        created_by TEXT,
                        source_message_id TEXT,
                        completed_at TEXT,
                        cancelled_at TEXT
                    )
                    """
                )

            initialize_database(db_path)
            task = create_scheduled_task(
                channel_id="123",
                message="migrated",
                due_at=datetime(2026, 6, 1, 9, 0, tzinfo=UTC),
                db_path=db_path,
            )

        self.assertEqual(task.kind, SCHEDULE_KIND_POST)
        self.assertIsNone(task.note)

    def test_mark_done_and_cancel_only_update_pending_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "local.sqlite3"
            done_task = create_scheduled_task(
                channel_id="123",
                message="done",
                due_at=datetime(2026, 6, 1, 9, 0, tzinfo=UTC),
                db_path=db_path,
            )
            cancelled_task = create_scheduled_task(
                channel_id="123",
                message="cancelled",
                due_at=datetime(2026, 6, 1, 9, 0, tzinfo=UTC),
                db_path=db_path,
            )

            done_task = mark_scheduled_task_done(
                done_task.id,
                db_path=db_path,
                now=datetime(2026, 6, 1, 10, 0, tzinfo=UTC),
            )
            done_task_after_cancel = cancel_scheduled_task(done_task.id, db_path=db_path)
            cancelled_task = cancel_scheduled_task(
                cancelled_task.id,
                db_path=db_path,
                now=datetime(2026, 6, 1, 10, 5, tzinfo=UTC),
            )

        self.assertIsNotNone(done_task)
        assert done_task is not None
        self.assertEqual(done_task.status, SCHEDULE_STATUS_DONE)
        self.assertEqual(done_task.completed_at, "2026-06-01T10:00:00+00:00")
        self.assertEqual(done_task_after_cancel, done_task)
        self.assertIsNotNone(cancelled_task)
        assert cancelled_task is not None
        self.assertEqual(cancelled_task.status, SCHEDULE_STATUS_CANCELLED)
        self.assertEqual(cancelled_task.cancelled_at, "2026-06-01T10:05:00+00:00")

    def test_utc_isoformat_treats_naive_as_utc(self) -> None:
        self.assertEqual(
            utc_isoformat(datetime(2026, 6, 1, 12, 0)),
            "2026-06-01T12:00:00+00:00",
        )


if __name__ == "__main__":
    unittest.main()
