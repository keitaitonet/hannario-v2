import os
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from hannario.bot import (
    DEFAULT_CHANNEL_SUMMARY_MAX_AGE_SECONDS,
    DEFAULT_CONTEXT_MESSAGE_LIMIT,
    MAX_CONTEXT_MESSAGE_LIMIT,
    channel_summary_max_age_seconds,
    context_message_limit,
    include_channel_summary,
    is_channel_summary_fresh,
)


class ContextMessageLimitTest(unittest.TestCase):
    def test_default_context_limit(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(context_message_limit(), DEFAULT_CONTEXT_MESSAGE_LIMIT)

    def test_context_limit_can_be_disabled(self) -> None:
        with patch.dict(os.environ, {"DISCORD_CONTEXT_MESSAGE_LIMIT": "0"}):
            self.assertEqual(context_message_limit(), 0)

    def test_context_limit_is_capped(self) -> None:
        with patch.dict(os.environ, {"DISCORD_CONTEXT_MESSAGE_LIMIT": "999"}):
            self.assertEqual(context_message_limit(), MAX_CONTEXT_MESSAGE_LIMIT)

    def test_invalid_context_limit_uses_default(self) -> None:
        with (
            patch.dict(os.environ, {"DISCORD_CONTEXT_MESSAGE_LIMIT": "many"}),
            patch("hannario.bot.logging.warning"),
        ):
            self.assertEqual(context_message_limit(), DEFAULT_CONTEXT_MESSAGE_LIMIT)

    def test_include_channel_summary_defaults_to_false(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(include_channel_summary())

    def test_include_channel_summary_accepts_truthy_values(self) -> None:
        for value in ("1", "true", "yes", "on", " TRUE "):
            with self.subTest(value=value), patch.dict(
                os.environ,
                {"DISCORD_INCLUDE_CHANNEL_SUMMARY": value},
            ):
                self.assertTrue(include_channel_summary())

    def test_include_channel_summary_rejects_other_values(self) -> None:
        for value in ("0", "false", "no", ""):
            with self.subTest(value=value), patch.dict(
                os.environ,
                {"DISCORD_INCLUDE_CHANNEL_SUMMARY": value},
            ):
                self.assertFalse(include_channel_summary())

    def test_channel_summary_max_age_defaults_to_one_hour(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                channel_summary_max_age_seconds(),
                DEFAULT_CHANNEL_SUMMARY_MAX_AGE_SECONDS,
            )

    def test_channel_summary_max_age_reads_env(self) -> None:
        with patch.dict(os.environ, {"DISCORD_CHANNEL_SUMMARY_MAX_AGE_SECONDS": "120"}):
            self.assertEqual(channel_summary_max_age_seconds(), 120)

    def test_invalid_channel_summary_max_age_uses_default(self) -> None:
        with (
            patch.dict(os.environ, {"DISCORD_CHANNEL_SUMMARY_MAX_AGE_SECONDS": "bad"}),
            patch("hannario.bot.logging.warning"),
        ):
            self.assertEqual(
                channel_summary_max_age_seconds(),
                DEFAULT_CHANNEL_SUMMARY_MAX_AGE_SECONDS,
            )

    def test_channel_summary_freshness(self) -> None:
        now = datetime(2026, 5, 31, 10, 0, tzinfo=UTC)
        fresh_summary = {
            "created_at": (now - timedelta(minutes=30)).isoformat(),
        }
        stale_summary = {
            "created_at": (now - timedelta(hours=2)).isoformat(),
        }

        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(is_channel_summary_fresh(fresh_summary, now=now))
            self.assertFalse(is_channel_summary_fresh(stale_summary, now=now))


if __name__ == "__main__":
    unittest.main()
