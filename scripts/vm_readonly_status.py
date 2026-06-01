from __future__ import annotations

import argparse
import shlex
import subprocess
from dataclasses import dataclass


DEFAULT_HOST = "172.17.2.4"
DEFAULT_REPO_PATH = "/home/keitaito/hannario-v2"


@dataclass(frozen=True)
class RemoteSection:
    title: str
    command: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect read-only VM status over non-interactive SSH."
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--repo-path", default=DEFAULT_REPO_PATH)
    parser.add_argument("--connect-timeout", type=int, default=5)
    parser.add_argument("--journal-lines", type=int, default=80)
    return parser.parse_args()


def shell_join(commands: list[str]) -> str:
    return "\n".join(commands)


def build_remote_script(repo_path: str, journal_lines: int) -> str:
    repo = shlex.quote(repo_path)
    lines = shlex.quote(str(journal_lines))
    sections = [
        RemoteSection(
            "identity",
            shell_join(
                [
                    'printf "user=%s\\n" "$USER"',
                    'printf "home=%s\\n" "$HOME"',
                    'printf "pwd=%s\\n" "$PWD"',
                    "id",
                ]
            ),
        ),
        RemoteSection(
            "system",
            shell_join(
                [
                    "uname -a",
                    "test -f /etc/os-release && sed -n '1,8p' /etc/os-release || true",
                    "uptime",
                    "df -h /",
                    "free -h",
                ]
            ),
        ),
        RemoteSection(
            "commands",
            shell_join(
                [
                    "for cmd in git uv python3 docker systemctl journalctl; do "
                    'if command -v "$cmd" >/dev/null 2>&1; then '
                    'printf "%s=%s\\n" "$cmd" "$(command -v "$cmd")"; '
                    "else "
                    'printf "%s=missing\\n" "$cmd"; '
                    "fi; "
                    "done",
                ]
            ),
        ),
        RemoteSection(
            "repo",
            shell_join(
                [
                    f"if test -d {repo}; then",
                    f"  cd {repo}",
                    '  printf "repo_path=%s\\n" "$PWD"',
                    "  git status --short || true",
                    "  git log -1 --oneline || true",
                    "else",
                    f'  printf "repo_missing=%s\\n" {repo}',
                    "fi",
                ]
            ),
        ),
        RemoteSection(
            "user-systemd",
            shell_join(
                [
                    "systemctl --user status hannario-bot.service --no-pager || true",
                    "systemctl --user is-enabled hannario-bot.service 2>/dev/null || true",
                ]
            ),
        ),
        RemoteSection(
            "bot-journal",
            shell_join(
                [
                    "journalctl --user -u hannario-bot.service "
                    f"-n {lines} --no-pager 2>/dev/null || true",
                ]
            ),
        ),
        RemoteSection(
            "docker",
            shell_join(
                [
                    "if command -v docker >/dev/null 2>&1; then",
                    "  docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}' || true",
                    f"  if test -d {repo}; then",
                    f"    cd {repo}",
                    "    docker compose ps || true",
                    "    docker compose logs --tail 80 letta 2>/dev/null || true",
                    "  fi",
                    "else",
                    '  printf "docker=missing\\n"',
                    "fi",
                ]
            ),
        ),
    ]

    script_lines = ["set +e"]
    for section in sections:
        script_lines.append(f'printf "\\n## {section.title}\\n"')
        script_lines.append(section.command)
    return "\n".join(script_lines)


def run_ssh(host: str, script: str, connect_timeout: int) -> int:
    remote_command = "sh -lc " + shlex.quote(script)
    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={connect_timeout}",
        host,
        remote_command,
    ]
    completed = subprocess.run(command, text=True, check=False)
    return completed.returncode


def main() -> None:
    args = parse_args()
    script = build_remote_script(args.repo_path, args.journal_lines)
    raise SystemExit(run_ssh(args.host, script, args.connect_timeout))


if __name__ == "__main__":
    main()
