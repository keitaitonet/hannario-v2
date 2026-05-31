import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from summarize_channel_observations import extract_response_text, summary_instructions


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


if __name__ == "__main__":
    unittest.main()
