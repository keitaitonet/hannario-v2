import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from list_observed_channels import print_channel, read_channel_stats, update_channel_stats


class ListObservedChannelsTest(unittest.TestCase):
    def test_update_channel_stats(self) -> None:
        stats = {}

        update_channel_stats(
            stats,
            {
                "channel_id": "123",
                "channel_name": "general",
                "timestamp": "2026-05-31T00:00:00+00:00",
                "author_display_name": "alice",
            },
        )
        update_channel_stats(
            stats,
            {
                "channel_id": "123",
                "channel_name": "general",
                "timestamp": "2026-05-31T00:01:00+00:00",
                "author_display_name": "bob",
            },
        )

        self.assertEqual(stats["123"]["count"], 2)
        self.assertEqual(stats["123"]["first_observed_at"], "2026-05-31T00:00:00+00:00")
        self.assertEqual(stats["123"]["latest_observed_at"], "2026-05-31T00:01:00+00:00")
        self.assertEqual(stats["123"]["latest_author"], "bob")

    def test_read_channel_stats_sorts_by_latest(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        path = temp_dir / "observations.jsonl"
        try:
            path.write_text(
                "\n".join(
                    [
                        '{"channel_id":"1","channel_name":"old","timestamp":"2026-05-31T00:00:00+00:00"}',
                        '{"channel_id":"2","channel_name":"new","timestamp":"2026-05-31T00:01:00+00:00"}',
                    ]
                ),
                encoding="utf-8",
            )

            records = read_channel_stats(path)

            self.assertEqual([record["channel_id"] for record in records], ["2", "1"])
        finally:
            path.unlink(missing_ok=True)
            temp_dir.rmdir()

    def test_print_channel(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            print_channel(
                {
                    "channel_id": "123",
                    "channel_name": "general",
                    "count": 2,
                    "latest_observed_at": "2026-05-31T00:01:00+00:00",
                    "latest_author": "bob",
                }
            )

        self.assertIn("#general (123): 2 observations", output.getvalue())


if __name__ == "__main__":
    unittest.main()
