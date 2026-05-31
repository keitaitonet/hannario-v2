import argparse
import json


CANDIDATE_KEYWORDS = (
    "覚えて",
    "今後",
    "呼んで",
    "呼ぶ",
    "やめて",
    "嫌",
    "苦手",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a dry-run memory update proposal. Does not write memory.",
    )
    parser.add_argument(
        "conversation",
        help="Conversation text to inspect.",
    )
    return parser.parse_args()


def build_proposal(conversation: str) -> dict[str, str | None]:
    if any(keyword in conversation for keyword in CANDIDATE_KEYWORDS):
        return {
            "action": "append",
            "target": "playbook",
            "reason": "The conversation contains a possible durable preference signal.",
            "proposal": "TODO: write an ID-based proposal manually, e.g. P006: ...",
        }

    return {
        "action": "none",
        "target": None,
        "reason": "No obvious durable memory update signal was detected by the stub.",
        "proposal": None,
    }


def main() -> None:
    args = parse_args()
    proposal = build_proposal(args.conversation)
    print(json.dumps(proposal, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
