import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from show_recent_observations import (
    matches_channel_filter,
    print_record,
    read_recent_observation_records,
)


class RecentObservationsFormatTest(unittest.TestCase):
    def test_matches_channel_filter_by_name(self) -> None:
        record = {"channel_name": "general", "channel_id": "123"}

        self.assertTrue(matches_channel_filter(record, "general", None))
        self.assertFalse(matches_channel_filter(record, "random", None))

    def test_matches_channel_filter_by_id(self) -> None:
        record = {"channel_name": "general", "channel_id": "123"}

        self.assertTrue(matches_channel_filter(record, None, "123"))
        self.assertFalse(matches_channel_filter(record, None, "456"))

    def test_matches_channel_filter_by_name_and_id(self) -> None:
        record = {"channel_name": "general", "channel_id": "123"}

        self.assertTrue(matches_channel_filter(record, "general", "123"))
        self.assertFalse(matches_channel_filter(record, "general", "456"))

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

    def test_read_recent_observation_records_filters_before_limit(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        path = temp_dir / "observations.jsonl"
        try:
            path.write_text(
                "\n".join(
                    [
                        '{"channel_name":"general","channel_id":"1","clean_content":"a"}',
                        '{"channel_name":"random","channel_id":"2","clean_content":"b"}',
                        '{"channel_name":"general","channel_id":"1","clean_content":"c"}',
                    ]
                ),
                encoding="utf-8",
            )

            records = read_recent_observation_records(path, 2, channel="general")

            self.assertEqual([record["clean_content"] for record in records], ["a", "c"])
        finally:
            path.unlink(missing_ok=True)
            temp_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
