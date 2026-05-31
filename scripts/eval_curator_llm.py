from curator_llm_dry_run import build_proposal
from eval_curator_stub import load_examples


def main() -> None:
    examples = load_examples()
    passed = 0

    for item in examples:
        proposal = build_proposal(item["input"])
        actual = proposal.action
        expected = item["expected_action"]
        ok = actual == expected
        passed += int(ok)
        status = "PASS" if ok else "FAIL"
        print(f"{item['id']}: {status} expected={expected} actual={actual}")
        print(f"  reason={proposal.reason}")
        if proposal.proposal is not None:
            print(f"  proposal={proposal.proposal}")

    print(f"{passed}/{len(examples)} passed")

    if passed != len(examples):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
