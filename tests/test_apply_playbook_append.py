import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from apply_playbook_append import (
    apply_playbook_append,
    non_id_playbook_lines,
    normalize_playbook_body,
    proposal_from_json_text,
    similar_existing_playbook_line,
    validate_playbook_append,
)


class ApplyPlaybookAppendTest(unittest.TestCase):
    def test_validate_playbook_append(self) -> None:
        self.assertEqual(
            validate_playbook_append(" P006: ユーザーが希望した呼び方を尊重する。 "),
            "P006: ユーザーが希望した呼び方を尊重する。",
        )

    def test_validate_playbook_append_rejects_missing_id(self) -> None:
        with self.assertRaises(ValueError):
            validate_playbook_append("ユーザーが希望した呼び方を尊重する。")

    def test_validate_playbook_append_rejects_multiline(self) -> None:
        with self.assertRaises(ValueError):
            validate_playbook_append("P006: one\nP007: two")

    def test_apply_playbook_append(self) -> None:
        self.assertEqual(
            apply_playbook_append("P001: 既存ルール", "P002: 追加ルール"),
            "P001: 既存ルール\nP002: 追加ルール",
        )

    def test_non_id_playbook_lines(self) -> None:
        self.assertEqual(
            non_id_playbook_lines("raw rule\nP001: 既存ルール\n\nP002: 追加ルール"),
            ["raw rule"],
        )

    def test_apply_playbook_append_rejects_non_id_lines(self) -> None:
        with self.assertRaises(ValueError):
            apply_playbook_append("raw rule\nP001: 既存ルール", "P002: 追加ルール")

    def test_apply_playbook_append_rejects_duplicate_line(self) -> None:
        with self.assertRaises(ValueError):
            apply_playbook_append("P001: 既存ルール", "P001: 既存ルール")

    def test_normalize_playbook_body(self) -> None:
        self.assertEqual(
            normalize_playbook_body("ユーザーの指示に従い、古い要約より直近の会話を優先して答える。"),
            "古い要約より直近の会話を優先して答える",
        )

    def test_similar_existing_playbook_line(self) -> None:
        current_value = "P007: 古い要約より直近の会話を優先して答える。"
        proposal = "P008: ユーザーの指示に従い、古い要約より直近の会話を優先して答える。"

        self.assertEqual(
            similar_existing_playbook_line(current_value, proposal),
            "P007: 古い要約より直近の会話を優先して答える。",
        )

    def test_apply_playbook_append_rejects_similar_duplicate(self) -> None:
        with self.assertRaises(ValueError):
            apply_playbook_append(
                "P007: 古い要約より直近の会話を優先して答える。",
                "P008: ユーザーの指示に従い、古い要約より直近の会話を優先して答える。",
            )

    def test_proposal_from_json_text(self) -> None:
        text = """
        {
          "action": "append",
          "target": "playbook",
          "reason": "durable preference",
          "proposal": "P006: ユーザーが希望した呼び方を尊重する。"
        }
        """

        self.assertEqual(
            proposal_from_json_text(text),
            "P006: ユーザーが希望した呼び方を尊重する。",
        )

    def test_proposal_from_json_text_rejects_none(self) -> None:
        text = """
        {
          "action": "none",
          "target": null,
          "reason": "no durable update",
          "proposal": null
        }
        """

        with self.assertRaises(ValueError):
            proposal_from_json_text(text)


if __name__ == "__main__":
    unittest.main()
