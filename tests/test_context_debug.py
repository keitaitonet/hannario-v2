import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from show_context_debug import format_current_mention, format_saved_recent_context


class ContextDebugTest(unittest.TestCase):
    def test_format_current_mention(self) -> None:
        record = {
            "timestamp": "2026-05-31T00:00:00+00:00",
            "author_display_name": "alice",
            "author_id": "111",
            "clean_content": "どう思う？",
            "bot_reply": "そうだね",
        }

        text = format_current_mention(record)

        self.assertIn("mention:", text)
        self.assertIn("alice (111): どう思う？", text)
        self.assertIn("bot_reply: そうだね", text)

    def test_format_saved_recent_context(self) -> None:
        record = {
            "channel_name": "general",
            "channel_id": "123",
            "recent_context": [
                {
                    "timestamp": "2026-05-31T00:00:00+00:00",
                    "author_display_name": "bob",
                    "author_id": "222",
                    "clean_content": "前の話",
                }
            ],
        }

        text = format_saved_recent_context(record)

        self.assertIn("saved_discord_api_recent_context_oldest_first:", text)
        self.assertIn("channel: general (123)", text)
        self.assertIn("bob (222): 前の話", text)


if __name__ == "__main__":
    unittest.main()
