import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

from curator_llm_dry_run import DEFAULT_CURATOR_MODEL, load_openai_env
from show_channel_context import format_channel_context, require_channel_filter
from show_recent_observations import (
    DEFAULT_OBSERVATION_LOG_PATH,
    read_recent_observation_records,
)


DEFAULT_SUMMARY_MODEL = DEFAULT_CURATOR_MODEL
DEFAULT_SUMMARY_LOG_PATH = Path("logs/channel_summaries.jsonl")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize observed non-mention messages for one Discord channel. "
            "Does not write memory."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of recent observed channel records to summarize.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_OBSERVATION_LOG_PATH,
        help="Path to the observation JSONL log.",
    )
    parser.add_argument(
        "--channel",
        help="Summarize records from this channel name.",
    )
    parser.add_argument(
        "--channel-id",
        help="Summarize records from this Discord channel ID.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Append the summary result to logs/channel_summaries.jsonl.",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=DEFAULT_SUMMARY_LOG_PATH,
        help="Path to write JSONL summaries when --save is used.",
    )
    return parser.parse_args()


def summary_instructions() -> str:
    return """You summarize observed Discord channel context for a small private companion bot.

The input contains observed non-mention messages from one Discord channel.
Do not propose memory writes.
Do not invent facts outside the input.
Keep the output in Japanese.

Return:
- 概要: 1-2 short sentences.
- 話題: concise bullet list of main topics.
- 継続中の文脈: anything that may matter if the bot is mentioned soon.
"""


def extract_response_text(response: object) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()
    raise RuntimeError(f"Could not extract summary text from {type(response)!r}")


def summarize_context(context: str) -> str:
    load_openai_env()
    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL),
        instructions=summary_instructions(),
        input=context,
        temperature=0,
    )
    return extract_response_text(response)


def summary_log_record(
    records: list[dict[str, Any]],
    context: str,
    summary: str,
    *,
    model: str,
) -> dict[str, Any]:
    first = records[0]
    last = records[-1]
    return {
        "created_at": datetime.now(UTC).isoformat(),
        "channel_id": str(last.get("channel_id")) if last.get("channel_id") else None,
        "channel_name": last.get("channel_name"),
        "record_count": len(records),
        "first_observed_at": first.get("timestamp"),
        "last_observed_at": last.get("timestamp"),
        "model": model,
        "context": context,
        "summary": summary,
    }


def save_summary(
    path: Path,
    records: list[dict[str, Any]],
    context: str,
    summary: str,
    *,
    model: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    record = summary_log_record(
        records,
        context,
        summary,
        model=model,
    )
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
        file.write("\n")


def main() -> None:
    args = parse_args()
    require_channel_filter(args.channel, args.channel_id)

    try:
        records = read_recent_observation_records(
            args.path,
            args.limit,
            channel=args.channel,
            channel_id=args.channel_id,
        )
    except FileNotFoundError:
        print(f"No observation log found at {args.path}. Run the bot first.")
        return

    if not records:
        print(f"No matching observation records found in {args.path}.")
        return

    context = format_channel_context(
        records,
        channel=args.channel,
        channel_id=args.channel_id,
    )
    print("Input:")
    print(context)
    print()
    summary = summarize_context(context)
    print("Summary:")
    print(summary)
    print()
    if args.save:
        model = os.getenv("SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL)
        save_summary(args.summary_path, records, context, summary, model=model)
        print(f"Summary saved to {args.summary_path}.")
    print("No memory was written.")


if __name__ == "__main__":
    main()
