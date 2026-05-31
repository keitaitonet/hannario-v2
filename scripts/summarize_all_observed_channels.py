import argparse
import os
from pathlib import Path

from list_observed_channels import read_channel_stats
from show_channel_context import format_channel_context
from show_recent_observations import (
    DEFAULT_OBSERVATION_LOG_PATH,
    read_recent_observation_records,
)
from summarize_channel_observations import (
    DEFAULT_SUMMARY_LOG_PATH,
    DEFAULT_SUMMARY_MODEL,
    save_summary,
    summarize_context,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize observed non-mention messages for every observed Discord "
            "channel. Does not write memory."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of recent observed records to summarize per channel.",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_OBSERVATION_LOG_PATH,
        help="Path to the observation JSONL log.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Append summary results to logs/channel_summaries.jsonl.",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=DEFAULT_SUMMARY_LOG_PATH,
        help="Path to write JSONL summaries when --save is used.",
    )
    parser.add_argument(
        "--max-channels",
        type=int,
        help="Only summarize this many channels, ordered by latest observation.",
    )
    return parser.parse_args()


def selected_channels(
    channels: list[dict],
    max_channels: int | None,
) -> list[dict]:
    if max_channels is None:
        return channels
    if max_channels <= 0:
        raise ValueError("max_channels must be positive.")
    return channels[:max_channels]


def summarize_channel(
    observation_path: Path,
    channel: dict,
    limit: int,
    *,
    save: bool,
    summary_path: Path,
) -> str:
    channel_id = str(channel["channel_id"])
    channel_name = channel.get("channel_name")
    records = read_recent_observation_records(
        observation_path,
        limit,
        channel_id=channel_id,
    )
    context = format_channel_context(
        records,
        channel=channel_name,
        channel_id=channel_id,
    )
    summary = summarize_context(context)

    output = [
        f"## {channel_name or 'unknown-channel'} ({channel_id})",
        f"records={len(records)}",
        summary,
    ]

    if save:
        save_summary(
            summary_path,
            records,
            context,
            summary,
            model=os.getenv("SUMMARY_MODEL", DEFAULT_SUMMARY_MODEL),
        )
        output.append(f"Saved to {summary_path}.")

    return "\n".join(output)


def main() -> None:
    args = parse_args()

    try:
        channels = read_channel_stats(args.path)
    except FileNotFoundError:
        print(f"No observation log found at {args.path}. Run the bot first.")
        return

    if not channels:
        print(f"No observations found in {args.path}.")
        return

    try:
        channels = selected_channels(channels, args.max_channels)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    for index, channel in enumerate(channels):
        if index:
            print()
        print(
            summarize_channel(
                args.path,
                channel,
                args.limit,
                save=args.save,
                summary_path=args.summary_path,
            )
        )

    print()
    print("No memory was written.")


if __name__ == "__main__":
    main()
