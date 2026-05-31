import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime


DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 900
TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class HeartbeatConfig:
    enabled: bool = False
    interval_seconds: int = DEFAULT_HEARTBEAT_INTERVAL_SECONDS


@dataclass(frozen=True)
class HeartbeatResult:
    checked_at: str


def parse_bool_env(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in TRUTHY_ENV_VALUES


def parse_positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        logging.warning("Invalid %s=%r; using %d", name, raw_value, default)
        return default

    if value <= 0:
        logging.warning("Invalid %s=%r; using %d", name, raw_value, default)
        return default
    return value


def load_heartbeat_config_from_env() -> HeartbeatConfig:
    return HeartbeatConfig(
        enabled=parse_bool_env("DISCORD_HEARTBEAT_ENABLED"),
        interval_seconds=parse_positive_int_env(
            "DISCORD_HEARTBEAT_INTERVAL_SECONDS",
            DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
        ),
    )


def run_heartbeat_once(now: datetime | None = None) -> HeartbeatResult:
    actual_now = now or datetime.now(UTC)
    if actual_now.tzinfo is None:
        actual_now = actual_now.replace(tzinfo=UTC)
    checked_at = actual_now.astimezone(UTC).isoformat()
    logging.info("Discord heartbeat tick checked_at=%s", checked_at)
    return HeartbeatResult(checked_at=checked_at)
