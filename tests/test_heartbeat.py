import os
import unittest
from datetime import UTC, datetime
from unittest.mock import patch

from heartbeat import (
    DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
    HeartbeatConfig,
    load_heartbeat_config_from_env,
    parse_positive_int_env,
    run_heartbeat_once,
)


class HeartbeatTest(unittest.TestCase):
    def test_load_heartbeat_config_defaults_disabled(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = load_heartbeat_config_from_env()

        self.assertEqual(
            config,
            HeartbeatConfig(
                enabled=False,
                interval_seconds=DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
            ),
        )

    def test_load_heartbeat_config_from_env(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DISCORD_HEARTBEAT_ENABLED": "1",
                "DISCORD_HEARTBEAT_INTERVAL_SECONDS": "30",
            },
        ):
            config = load_heartbeat_config_from_env()

        self.assertTrue(config.enabled)
        self.assertEqual(config.interval_seconds, 30)

    def test_parse_positive_int_env_uses_default_for_invalid_value(self) -> None:
        with (
            patch.dict(os.environ, {"TEST_INTERVAL": "bad"}),
            patch("heartbeat.logging.warning"),
        ):
            self.assertEqual(parse_positive_int_env("TEST_INTERVAL", 10), 10)

    def test_run_heartbeat_once_logs_current_time(self) -> None:
        now = datetime(2026, 5, 31, 0, 0, tzinfo=UTC)

        with patch("heartbeat.logging.info") as log_info:
            result = run_heartbeat_once(now)

        self.assertEqual(result.checked_at, "2026-05-31T00:00:00+00:00")
        log_info.assert_called_once_with(
            "Discord heartbeat tick checked_at=%s",
            "2026-05-31T00:00:00+00:00",
        )


if __name__ == "__main__":
    unittest.main()
