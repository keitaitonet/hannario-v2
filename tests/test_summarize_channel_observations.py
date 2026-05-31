import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from summarize_channel_observations import (
    extract_response_text,
    summary_instructions,
    summary_log_record,
)


class SummarizeChannelObservationsTest(unittest.TestCase):
    def test_summary_instructions_are_dry_run(self) -> None:
        instructions = summary_instructions()

        self.assertIn("Do not propose memory writes.", instructions)
        self.assertIn("Keep the output in Japanese.", instructions)

    def test_extract_response_text(self) -> None:
        response = SimpleNamespace(output_text="  要約です  ")

        self.assertEqual(extract_response_text(response), "要約です")

    def test_extract_response_text_rejects_empty_text(self) -> None:
        response = SimpleNamespace(output_text="")

        with self.assertRaises(RuntimeError):
            extract_response_text(response)

    def test_summary_log_record(self) -> None:
        records = [
            {
                "timestamp": "2026-05-31T00:00:00+00:00",
                "channel_id": "123",
                "channel_name": "general",
            },
            {
                "timestamp": "2026-05-31T00:01:00+00:00",
                "channel_id": "123",
                "channel_name": "general",
            },
        ]

        record = summary_log_record(
            records,
            "context text",
            "summary text",
            model="test-model",
        )

        self.assertEqual(record["channel_id"], "123")
        self.assertEqual(record["channel_name"], "general")
        self.assertEqual(record["record_count"], 2)
        self.assertEqual(record["first_observed_at"], "2026-05-31T00:00:00+00:00")
        self.assertEqual(record["last_observed_at"], "2026-05-31T00:01:00+00:00")
        self.assertEqual(record["model"], "test-model")
        self.assertEqual(record["context"], "context text")
        self.assertEqual(record["summary"], "summary text")
        self.assertIn("created_at", record)


if __name__ == "__main__":
    unittest.main()
