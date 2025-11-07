"""Command line interface for exploring the AI Learning Studio roadmap."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from textwrap import indent
from typing import Sequence

from .planning import default_phases, find_phase, next_phase

AUTO_SYNC_ENV_VAR = "AI_LEARNING_STUDIO_AUTO_PULL"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "AI Learning Studio helper. List available learning phases or show "
            "details for a specific one. Set AI_LEARNING_STUDIO_AUTO_PULL=1 to "
            "automatically sync the Git repository before loading phases."
        )
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available phases with their focus areas.",
    )
    parser.add_argument(
        "--phase",
        type=int,
        help="Display details for a single phase by its number.",
    )
    parser.add_argument(
        "--next",
        action="store_true",
        help=(
            "Show the next recommended phase. Optionally combine with --after to "
            "specify the last completed phase number."
        ),
    )
    parser.add_argument(
        "--after",
        type=int,
        help="Phase number that has already been completed when using --next.",
    )
    return parser


def _is_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _run_git_command(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        check=True,
        text=True,
    )


def maybe_auto_sync_repository(repo_path: Path | None = None) -> None:
    """Fetch and pull the latest changes when opt-in is enabled."""

    if not _is_truthy(os.environ.get(AUTO_SYNC_ENV_VAR)):
        return

    path = Path.cwd() if repo_path is None else repo_path

    try:
        result = _run_git_command(["rev-parse", "--is-inside-work-tree"], cwd=path)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return

    if result.stdout.strip().lower() != "true":
        return

    try:
        _run_git_command(["fetch", "--all"], cwd=path)
        _run_git_command(["pull"], cwd=path)
    except FileNotFoundError as exc:
        print(f"[auto-sync] Git executable not found: {exc}", file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() if exc.stderr else str(exc)
        print(f"[auto-sync] Git command failed: {message}", file=sys.stderr)


def render_phase_summary() -> str:
    phases = default_phases()
    lines = ["AI Learning Studio roadmap:"]
    for phase in phases:
        lines.append(f"- Phase {phase.number}: {phase.name} — {phase.focus}")
    lines.append("\nUse --phase <number> for more details.")
    return "\n".join(lines)


def render_phase_details(phase_number: int) -> str:
    phase = find_phase(default_phases(), phase_number)
    bullet_points = "\n".join(f"- {item}" for item in phase.highlights)
    return (
        f"Phase {phase.number}: {phase.name}\n"
        f"Focus: {phase.focus}\n\n"
        f"Key activities:\n{indent(bullet_points, '  ')}"
    )


def render_next_phase(after: int | None = None) -> str:
    phase = next_phase(default_phases(), after=after)
    bullet_points = "\n".join(f"- {item}" for item in phase.highlights)
    if after is None:
        context = "Starting point"
    else:
        context = f"Next step after completing Phase {after}"
    return (
        f"{context}: Phase {phase.number} – {phase.name}\n"
        f"Focus: {phase.focus}\n\n"
        f"Immediate tasks:\n{indent(bullet_points, '  ')}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    maybe_auto_sync_repository()

    if args.list and args.phase is not None:
        parser.error("--list cannot be combined with --phase")

    if args.next and args.phase is not None:
        parser.error("--next cannot be combined with --phase")

    if args.after is not None and not args.next:
        parser.error("--after requires --next")

    if args.list:
        print(render_phase_summary())
        return 0

    if args.phase is not None:
        print(render_phase_details(args.phase))
        return 0

    if args.next:
        print(render_next_phase(after=args.after))
        return 0

    print(render_phase_summary())
    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation guard
    raise SystemExit(main())
