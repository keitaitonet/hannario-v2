from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_PATHS = [
    Path("data/local.sqlite3"),
    Path("logs"),
    Path("memory_snapshots"),
    Path(".env"),
    Path(".env.letta"),
]


@dataclass(frozen=True)
class InventoryItem:
    path: Path
    exists: bool
    kind: str
    size_bytes: int
    file_count: int
    latest_mtime: float | None
    secret: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show read-only backup inventory for local durable state.",
    )
    parser.add_argument(
        "--path",
        action="append",
        type=Path,
        dest="paths",
        help="Path to include. Can be passed multiple times.",
    )
    return parser.parse_args()


def is_secret_path(path: Path) -> bool:
    return path.name in {".env", ".env.letta"}


def scan_path(path: Path) -> InventoryItem:
    if not path.exists():
        return InventoryItem(
            path=path,
            exists=False,
            kind="missing",
            size_bytes=0,
            file_count=0,
            latest_mtime=None,
            secret=is_secret_path(path),
        )

    if path.is_file():
        stat = path.stat()
        return InventoryItem(
            path=path,
            exists=True,
            kind="file",
            size_bytes=stat.st_size,
            file_count=1,
            latest_mtime=stat.st_mtime,
            secret=is_secret_path(path),
        )

    if path.is_dir():
        total_size = 0
        file_count = 0
        latest_mtime = path.stat().st_mtime
        for root, _dirs, files in os.walk(path):
            root_path = Path(root)
            for filename in files:
                file_path = root_path / filename
                try:
                    stat = file_path.stat()
                except OSError:
                    continue
                total_size += stat.st_size
                file_count += 1
                latest_mtime = max(latest_mtime, stat.st_mtime)
        return InventoryItem(
            path=path,
            exists=True,
            kind="dir",
            size_bytes=total_size,
            file_count=file_count,
            latest_mtime=latest_mtime,
            secret=is_secret_path(path),
        )

    stat = path.stat()
    return InventoryItem(
        path=path,
        exists=True,
        kind="other",
        size_bytes=0,
        file_count=0,
        latest_mtime=stat.st_mtime,
        secret=is_secret_path(path),
    )


def human_size(size_bytes: int) -> str:
    units = ["B", "KiB", "MiB", "GiB"]
    value = float(size_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size_bytes} B"


def format_mtime(timestamp: float | None) -> str:
    if timestamp is None:
        return "-"
    from datetime import UTC, datetime

    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def print_inventory(items: list[InventoryItem]) -> None:
    print("# Backup Inventory")
    for item in items:
        status = "present" if item.exists else "missing"
        secret_note = " secret" if item.secret else ""
        print(f"- {item.path}: {status} {item.kind}{secret_note}")
        print(f"  size: {human_size(item.size_bytes)}")
        print(f"  files: {item.file_count}")
        print(f"  latest_mtime: {format_mtime(item.latest_mtime)}")

    missing = [item.path for item in items if not item.exists]
    if missing:
        print()
        print("Missing backup targets:")
        for path in missing:
            print(f"- {path}")


def main() -> None:
    args = parse_args()
    paths = args.paths or DEFAULT_PATHS
    print_inventory([scan_path(path) for path in paths])


if __name__ == "__main__":
    main()
