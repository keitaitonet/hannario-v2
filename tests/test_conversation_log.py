import unittest
from datetime import UTC, datetime
from types import SimpleNamespace

from conversation_log import mention_log_record


def fake_message(
    content: str,
    *,
    message_id: int = 100,
    author_name: str = "alice",
    author_id: int = 111,
    created_at: datetime | None = None,
) -> SimpleNamespace:
    guild = SimpleNamespace(id=1, name="test-guild")
    channel = SimpleNamespace(id=2, name="general")
    author = SimpleNamespace(id=author_id, display_name=author_name)
    return SimpleNamespace(
        id=message_id,
        content=content,
        guild=guild,
        channel=channel,
        author=author,
        created_at=created_at or datetime(2026, 5, 31, tzinfo=UTC),
    )


class ConversationLogTest(unittest.TestCase):
    def test_mention_log_record_includes_recent_context(self) -> None:
        bot_user = SimpleNamespace(id=999)
        recent_messages = [
            fake_message("前の話", message_id=101, author_name="bob", author_id=222),
            fake_message(
                "<@999> botの返事",
                message_id=102,
                author_name="bot",
                author_id=999,
            ),
        ]
        current_message = fake_message(
            "<@999> 今の話は？",
            message_id=103,
            author_name="alice",
            author_id=111,
        )

        record = mention_log_record(
            current_message,
            bot_user,
            "前の話です",
            recent_messages=recent_messages,
        )

        self.assertEqual(record["message_id"], "103")
        self.assertEqual(record["clean_content"], "今の話は？")
        self.assertEqual(record["bot_reply"], "前の話です")
        self.assertEqual(
            record["recent_context"],
            [
                {
                    "timestamp": "2026-05-31T00:00:00+00:00",
                    "message_id": "101",
                    "author_id": "222",
                    "author_display_name": "bob",
                    "clean_content": "前の話",
                },
                {
                    "timestamp": "2026-05-31T00:00:00+00:00",
                    "message_id": "102",
                    "author_id": "999",
                    "author_display_name": "bot",
                    "clean_content": "botの返事",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
