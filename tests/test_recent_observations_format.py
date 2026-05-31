import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from show_recent_observations import print_record


class RecentObservationsFormatTest(unittest.TestCase):
    def test_print_record(self) -> None:
        record = {
            "timestamp": "2026-05-31T00:00:00+00:00",
            "channel_name": "general",
            "author_display_name": "alice",
            "clean_content": "こんにちは",
        }
        output = io.StringIO()

        with redirect_stdout(output):
            print_record(record)

        text = output.getvalue()
        self.assertIn("[2026-05-31T00:00:00+00:00] #general / alice", text)
        self.assertIn("Message: こんにちは", text)


if __name__ == "__main__":
    unittest.main()
