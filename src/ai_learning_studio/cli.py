"""Command line interface for exploring the AI Learning Studio roadmap."""

from __future__ import annotations

import argparse
from textwrap import indent

from .planning import default_phases, find_phase, next_phase


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "AI Learning Studio helper. List available learning phases or show "
            "details for a specific one."
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
