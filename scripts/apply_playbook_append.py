import argparse
import re

from dotenv import load_dotenv
from letta_client import Letta

from curator_memory import require_agent_id
from letta_settings import letta_base_url
from preview_memory_apply import append_preview


PLAYBOOK_LINE_PATTERN = re.compile(r"^P\d{3}:\s+\S")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append one reviewed playbook proposal to Letta memory.",
    )
    parser.add_argument(
        "proposal",
        help="Full playbook line to append, e.g. 'P006: ...'.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Apply without interactive confirmation.",
    )
    return parser.parse_args()


def validate_playbook_append(proposal: str) -> str:
    normalized = proposal.strip()
    if not normalized:
        raise ValueError("Proposal must not be empty.")
    if "\n" in normalized:
        raise ValueError("Proposal must be a single playbook line.")
    if not PLAYBOOK_LINE_PATTERN.match(normalized):
        raise ValueError("Proposal must start with a stable ID like 'P006: ...'.")
    return normalized


def apply_playbook_append(
    current_value: str,
    proposal: str,
) -> str:
    return append_preview(current_value, validate_playbook_append(proposal))


def confirm_apply(proposal: str) -> None:
    confirmation = input(f"Type 'append {proposal.split(':', 1)[0]}' to confirm: ")
    if confirmation != f"append {proposal.split(':', 1)[0]}":
        raise SystemExit("Aborted.")


def main() -> None:
    load_dotenv()
    args = parse_args()
    proposal = validate_playbook_append(args.proposal)

    agent_id = require_agent_id()
    client = Letta(base_url=letta_base_url())
    current_block = client.agents.blocks.retrieve(
        agent_id=agent_id,
        block_label="playbook",
    )
    new_value = apply_playbook_append(current_block.value, proposal)

    print(f"agent_id={agent_id}")
    print("block_label=playbook")
    print()
    print("Proposal:")
    print(proposal)
    print()
    print("Preview:")
    print(new_value)
    print()
    print("This will append one line to the playbook block.")

    if not args.yes:
        confirm_apply(proposal)

    updated_block = client.agents.blocks.modify(
        agent_id=agent_id,
        block_label="playbook",
        value=new_value,
    )

    print()
    print("Updated value:")
    print(updated_block.value)


if __name__ == "__main__":
    main()
