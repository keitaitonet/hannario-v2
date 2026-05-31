import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from bot import run_due_scheduled_tasks_once, send_channel_message
from schedule_db import create_scheduled_task, get_scheduled_task
from schedule_runner import ScheduleConfig


class FakeChannel:
    def __init__(self) -> None:
        self.sent_messages: list[str] = []

    async def send(self, message: str) -> None:
        self.sent_messages.append(message)


class FakeClient:
    def __init__(self, channel: FakeChannel | None = None) -> None:
        self.channel = channel

    def get_channel(self, channel_id: int) -> FakeChannel | None:
        if channel_id == 123:
            return self.channel
        return None

    async def fetch_channel(self, channel_id: int) -> FakeChannel | None:
        if channel_id == 123:
            return self.channel
        return None


class ScheduleBotTest(unittest.IsolatedAsyncioTestCase):
    async def test_send_channel_message_sends_to_channel(self) -> None:
        channel = FakeChannel()
        client = FakeClient(channel)

        result = await send_channel_message(client, "123", "hello")  # type: ignore[arg-type]

        self.assertTrue(result.should_post)
        self.assertEqual(result.reason, "ok")
        self.assertEqual(channel.sent_messages, ["hello"])

    async def test_send_channel_message_rejects_invalid_channel_id(self) -> None:
        result = await send_channel_message(FakeClient(), "not-a-number", "hello")  # type: ignore[arg-type]

        self.assertFalse(result.should_post)
        self.assertEqual(result.reason, "invalid_channel_id")

    async def test_run_due_scheduled_tasks_posts_due_tasks_and_marks_done(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "local.sqlite3"
            log_path = Path(temp_dir) / "scheduled_tasks.jsonl"
            task = create_scheduled_task(
                channel_id="123",
                message="due message",
                due_at=datetime.now(UTC) - timedelta(minutes=1),
                db_path=db_path,
            )
            create_scheduled_task(
                channel_id="123",
                message="future message",
                due_at=datetime.now(UTC) + timedelta(hours=1),
                db_path=db_path,
            )
            channel = FakeChannel()
            config = ScheduleConfig(
                enabled=True,
                db_path=db_path,
                log_path=log_path,
            )

            await run_due_scheduled_tasks_once(config, FakeClient(channel))  # type: ignore[arg-type]

            updated_task = get_scheduled_task(task.id, db_path=db_path)
            log_text = log_path.read_text(encoding="utf-8")

        self.assertEqual(channel.sent_messages, ["due message"])
        self.assertIsNotNone(updated_task)
        assert updated_task is not None
        self.assertEqual(updated_task.status, "done")
        self.assertIn('"should_send": true', log_text)
        self.assertIn('"status_after": "done"', log_text)


if __name__ == "__main__":
    unittest.main()
