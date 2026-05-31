import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from show_channel_context import format_channel_context, require_channel_filter


class ChannelContextTest(unittest.TestCase):
    def test_require_channel_filter(self) -> None:
        with self.assertRaises(SystemExit):
            require_channel_filter(None, None)

        require_channel_filter("general", None)
        require_channel_filter(None, "123")

    def test_format_channel_context(self) -> None:
        records = [
            {
                "timestamp": "2026-05-31T00:00:00+00:00",
                "channel_name": "general",
                "channel_id": "123",
                "author_display_name": "alice",
                "author_id": "111",
                "clean_content": "こんにちは",
            },
            {
                "timestamp": "2026-05-31T00:01:00+00:00",
                "channel_name": "general",
                "channel_id": "123",
                "author_display_name": "bob",
                "author_id": "222",
                "clean_content": "天気の話です",
            },
        ]

        text = format_channel_context(records)

        self.assertIn("observed_same_channel_context_oldest_first:", text)
        self.assertIn("channel: general (123)", text)
        self.assertIn("alice (111): こんにちは", text)
        self.assertIn("bob (222): 天気の話です", text)


if __name__ == "__main__":
    unittest.main()
