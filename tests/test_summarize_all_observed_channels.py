import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from summarize_all_observed_channels import selected_channels


class SummarizeAllObservedChannelsTest(unittest.TestCase):
    def test_selected_channels_without_limit(self) -> None:
        channels = [{"channel_id": "1"}, {"channel_id": "2"}]

        self.assertEqual(selected_channels(channels, None), channels)

    def test_selected_channels_with_limit(self) -> None:
        channels = [{"channel_id": "1"}, {"channel_id": "2"}]

        self.assertEqual(selected_channels(channels, 1), [{"channel_id": "1"}])

    def test_selected_channels_rejects_non_positive_limit(self) -> None:
        with self.assertRaises(ValueError):
            selected_channels([{"channel_id": "1"}], 0)


if __name__ == "__main__":
    unittest.main()
