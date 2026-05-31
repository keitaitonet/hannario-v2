import json
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from letta_client import Letta

from curator_memory import require_agent_id
from letta_settings import letta_base_url


DEFAULT_SNAPSHOT_DIR = Path("memory_snapshots")


def snapshot_path(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat()
    safe_timestamp = timestamp.replace("+00:00", "Z").replace(":", "-")
    return snapshot_dir / f"{safe_timestamp}.json"


def build_snapshot() -> dict:
    load_dotenv()

    client = Letta(base_url=letta_base_url())
    agent = client.agents.retrieve(require_agent_id(), include_relationships="memory")

    blocks = {}
    if agent.memory is not None:
        blocks = {
            block.label: {
                "id": block.id,
                "value": block.value,
            }
            for block in agent.memory.blocks
        }

    return {
        "created_at": datetime.now(UTC).isoformat(),
        "agent_id": agent.id,
        "name": agent.name,
        "blocks": blocks,
    }


def main() -> None:
    path = snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_snapshot(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(path)


if __name__ == "__main__":
    main()
