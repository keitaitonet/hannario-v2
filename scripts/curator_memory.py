import os
import re

from dotenv import load_dotenv
from letta_client import Letta

from letta_settings import letta_base_url


PLAYBOOK_ID_PATTERN = re.compile(r"^P(?P<number>\d{3}):", re.MULTILINE)


def next_playbook_id(playbook_value: str) -> str:
    numbers = [
        int(match.group("number"))
        for match in PLAYBOOK_ID_PATTERN.finditer(playbook_value)
    ]
    next_number = max(numbers, default=0) + 1
    return f"P{next_number:03d}"


def get_playbook_value() -> str:
    load_dotenv()

    client = Letta(base_url=letta_base_url())
    block = client.agents.blocks.retrieve(
        agent_id=require_agent_id(),
        block_label="playbook",
    )
    return block.value


def require_agent_id() -> str:
    load_dotenv()

    agent_id = os.getenv("LETTA_AGENT_ID")
    if not agent_id:
        raise SystemExit("Missing LETTA_AGENT_ID. Add it to .env first.")
    return agent_id
