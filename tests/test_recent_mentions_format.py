import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from curate_recent_mentions import record_to_curator_text
from show_recent_mentions import print_curator_input, print_record


class RecentMentionsFormatTest(unittest.TestCase):
    def setUp(self) -> None:
        self.record = {
            "timestamp": "2026-05-31T00:00:00+00:00",
            "channel_name": "general",
            "author_display_name": "alice",
            "clean_content": "今の話は？",
            "bot_reply": "ラーメンの話です",
            "recent_context": [
                {
                    "author_display_name": "bob",
                    "clean_content": "今日はラーメンの話をしています",
                }
            ],
        }

    def test_print_record_includes_recent_context(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            print_record(self.record)

        text = output.getvalue()
        self.assertIn("Context:", text)
        self.assertIn("- bob: 今日はラーメンの話をしています", text)
        self.assertIn("User: 今の話は？", text)

    def test_print_curator_input_includes_recent_context(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            print_curator_input(self.record)

        text = output.getvalue()
        self.assertIn("直近文脈:", text)
        self.assertIn("- bob: 今日はラーメンの話をしています", text)
        self.assertIn("ユーザー: 今の話は？", text)

    def test_curator_text_includes_recent_context(self) -> None:
        text = record_to_curator_text(self.record)

        self.assertIn("直近文脈:", text)
        self.assertIn("- bob: 今日はラーメンの話をしています", text)
        self.assertIn("Bot: ラーメンの話です", text)


if __name__ == "__main__":
    unittest.main()
