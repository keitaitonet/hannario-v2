from dotenv import load_dotenv
from letta_client import Letta

from letta_settings import letta_base_url, letta_embedding, letta_model


def main() -> None:
    load_dotenv()

    client = Letta(base_url=letta_base_url())
    agent = client.agents.create(
        name="hannario-discord-bot",
        model=letta_model(),
        embedding=letta_embedding(),
        memory_blocks=[
            {
                "label": "persona",
                "value": (
                    "あなたは大学の友達サーバーにいる日本語の会話相手。"
                    "友達っぽいが出しゃばらず、短く自然に返す。"
                ),
            },
            {
                "label": "playbook",
                "value": (
                    "メンションされたときだけ返す。"
                    "まだテスト中なので、できることを誇張しない。"
                    "分からないことは分からないと言う。"
                ),
            },
            {
                "label": "server_context",
                "value": "20人ほどの大学の友達がいる単一 Discord サーバー。",
            },
        ],
    )

    print(f"LETTA_AGENT_ID={agent.id}")
    print("Add this line to .env.")


if __name__ == "__main__":
    main()
