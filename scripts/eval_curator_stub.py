import json
from pathlib import Path
from typing import Any

from curator_dry_run import build_proposal
from curator_memory import get_playbook_value


EXAMPLES_PATH = Path("data/curator_examples.jsonl")


def load_examples() -> list[dict[str, Any]]:
    examples = []
    for line_no, line in enumerate(EXAMPLES_PATH.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        item = json.loads(line)
        missing = {"id", "input", "expected_action"} - set(item)
        if missing:
            raise ValueError(f"{EXAMPLES_PATH}:{line_no} missing keys: {sorted(missing)}")
        examples.append(item)
    return examples


def main() -> None:
    examples = load_examples()
    playbook_value = get_playbook_value()
    passed = 0

    for item in examples:
        proposal = build_proposal(item["input"], playbook_value)
        actual = proposal.action
        expected = item["expected_action"]
        ok = actual == expected
        passed += int(ok)
        status = "PASS" if ok else "FAIL"
        print(f"{item['id']}: {status} expected={expected} actual={actual}")

    print(f"{passed}/{len(examples)} passed")

    if passed != len(examples):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
