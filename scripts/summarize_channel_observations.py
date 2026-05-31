import argparse
import os
from pathlib import Path

from openai import OpenAI

from curator_llm_dry_run import DEFAULT_CURATOR_MODEL, load_openai_env
from show_channel_context import format_channel_context, require_channel_filter
from show_recent_observations import (
    DEFAULT_OBSERVATION_LOG_PATH,
    read_recent_observation_records,
)


DEFAULT_SUMMARY_MODEL = DEFAULT_CURATOR_MODEL


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
    print("Summary:")
    print(summarize_context(context))
    print()
    print("No memory was written.")


if __name__ == "__main__":
    main()
