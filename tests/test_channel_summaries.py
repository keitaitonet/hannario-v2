import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from show_channel_summaries import print_record, read_recent_summary_records


class ChannelSummariesTest(unittest.TestCase):
    def test_print_record(self) -> None:
        record = {
            "created_at": "2026-05-31T00:10:00+00:00",
            "channel_name": "general",
            "record_count": 2,
            "first_observed_at": "2026-05-31T00:00:00+00:00",
            "last_observed_at": "2026-05-31T00:01:00+00:00",
            "model": "test-model",
            "summary": "要約です",
        }
        output = io.StringIO()

        with redirect_stdout(output):
            print_record(record)

        text = output.getvalue()
        self.assertIn("#general / 2 records / test-model", text)
        self.assertIn("Range: 2026-05-31T00:00:00+00:00 -> 2026-05-31T00:01:00+00:00", text)
        self.assertIn("要約です", text)

    def test_print_record_can_show_context(self) -> None:
        record = {"summary": "要約です", "context": "context text"}
        output = io.StringIO()

        with redirect_stdout(output):
            print_record(record, show_context=True)

        self.assertIn("context text", output.getvalue())

    def test_read_recent_summary_records_filters_before_limit(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        path = temp_dir / "summaries.jsonl"
        try:
            path.write_text(
                "\n".join(
                    [
                        '{"channel_name":"general","channel_id":"1","summary":"a"}',
                        '{"channel_name":"random","channel_id":"2","summary":"b"}',
                        '{"channel_name":"general","channel_id":"1","summary":"c"}',
                    ]
                ),
                encoding="utf-8",
            )

            records = read_recent_summary_records(path, 2, channel="general")

            self.assertEqual([record["summary"] for record in records], ["a", "c"])
        finally:
            path.unlink(missing_ok=True)
            temp_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
