import argparse
import os
import re

from dotenv import load_dotenv
from letta_client import Letta

from curator_schema import CuratorProposal
from letta_settings import letta_base_url


NICKNAME_KEYWORDS = ("呼んで", "呼ぶ")
AVOIDANCE_KEYWORDS = ("やめて", "嫌", "苦手")
DURABLE_PREFERENCE_KEYWORDS = ("覚えて", "今後")
PLAYBOOK_ID_PATTERN = re.compile(r"^P(?P<number>\d{3}):", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a dry-run memory update proposal. Does not write memory.",
    )
    parser.add_argument(
        "conversation",
        help="Conversation text to inspect.",
    )
    return parser.parse_args()


def next_playbook_id(playbook_value: str) -> str:
    numbers = [
        int(match.group("number"))
        for match in PLAYBOOK_ID_PATTERN.finditer(playbook_value)
    ]
    next_number = max(numbers, default=0) + 1
    return f"P{next_number:03d}"


def get_playbook_value() -> str:
    load_dotenv()

    agent_id = os.getenv("LETTA_AGENT_ID")
    if not agent_id:
        raise SystemExit("Missing LETTA_AGENT_ID. Add it to .env first.")

    client = Letta(base_url=letta_base_url())
    block = client.agents.blocks.retrieve(
        agent_id=agent_id,
        block_label="playbook",
    )
    return block.value


def classify_signal(conversation: str) -> tuple[str, str] | None:
    if any(keyword in conversation for keyword in NICKNAME_KEYWORDS):
        return (
            "The conversation contains a possible durable naming preference.",
            "ユーザーが希望した呼び方を尊重する。",
        )

    if any(keyword in conversation for keyword in AVOIDANCE_KEYWORDS):
        return (
            "The conversation contains a possible durable avoidance preference.",
            "ユーザーが嫌がった話題や振る舞いを避ける。",
        )

    if any(keyword in conversation for keyword in DURABLE_PREFERENCE_KEYWORDS):
        return (
            "The conversation contains a possible durable preference signal.",
            "ユーザーが明示した継続的な希望を尊重する。",
        )

    return None


def build_proposal(conversation: str, playbook_value: str) -> CuratorProposal:
    signal = classify_signal(conversation)
    if signal is not None:
        reason, proposal_text = signal
        playbook_id = next_playbook_id(playbook_value)
        return CuratorProposal(
            action="append",
            target="playbook",
            reason=reason,
            proposal=f"{playbook_id}: {proposal_text}",
        )

    return CuratorProposal(
        action="none",
        target=None,
        reason="No obvious durable memory update signal was detected by the stub.",
        proposal=None,
    )


def main() -> None:
    args = parse_args()
    playbook_value = get_playbook_value()
    proposal = build_proposal(args.conversation, playbook_value)
    print(proposal.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
