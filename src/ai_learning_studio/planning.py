"""Planning utilities for the AI Learning Studio roadmap."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

_MILESTONE_ENV_VAR = "AI_LEARNING_STUDIO_MILESTONES_DIR"
_MILESTONE_HEADER = re.compile(r"^#\s*Milestone\s+(?P<number>\d+)\s*[–-]\s*(?P<title>.+?)\s*$")


@dataclass(frozen=True)
class Phase:
    """Represents a single learning phase for the project."""

    number: int
    name: str
    focus: str
    highlights: List[str]

    def to_markdown(self) -> str:
        """Render the phase as a Markdown bullet list."""
        bullet_points = "\n".join(f"  - {item}" for item in self.highlights)
        return f"### Phase {self.number} – {self.name}\n{self.focus}\n\n{bullet_points}"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _milestone_directory() -> Path:
    """Return the directory that holds milestone documentation."""

    override = os.environ.get(_MILESTONE_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()
    return _project_root() / "docs" / "milestones"


def _collapse_lines(lines: List[str]) -> str:
    return " ".join(part.strip() for part in lines if part.strip())


def _extract_objective(lines: List[str]) -> str:
    capture = False
    collected: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## objective"):
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture:
            collected.append(line)
    if collected:
        return _collapse_lines(collected)
    # Fallback: first non-empty paragraph after the header.
    for line in lines:
        if line.strip() and not line.strip().startswith("#"):
            return line.strip()
    return "See milestone documentation for details."


def _extract_highlights(lines: List[str]) -> List[str]:
    highlights: List[str] = []
    capture = False
    for raw in lines:
        line = raw.strip()
        if not line:
            if capture and highlights:
                break
            continue
        if line.startswith(("- ", "* ")):
            capture = True
            highlights.append(line[2:].strip())
            continue
        match = re.match(r"^(\d+)\.\s+(.*)", line)
        if match:
            capture = True
            highlights.append(match.group(2).strip())
            continue
        if capture and highlights:
            break
    if highlights:
        return highlights
    return ["Consult the milestone file for recommended tasks."]


def _parse_milestone(path: Path) -> Phase:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"Milestone file '{path}' is empty")
    header = _MILESTONE_HEADER.match(lines[0].strip())
    if not header:
        raise ValueError(f"Milestone file '{path}' is missing a valid header")

    number = int(header.group("number"))
    name = header.group("title").strip()
    focus = _extract_objective(lines[1:])
    highlights = _extract_highlights(lines[1:])
    return Phase(number=number, name=name, focus=focus, highlights=highlights)


def default_phases() -> List[Phase]:
    """Return phases derived from the milestone documentation."""

    directory = _milestone_directory()
    if not directory.exists():
        raise FileNotFoundError(
            f"Milestone directory '{directory}' does not exist. "
            "Set AI_LEARNING_STUDIO_MILESTONES_DIR to override the path."
        )

    phases = [_parse_milestone(path) for path in sorted(directory.glob("*.md"))]
    if not phases:
        raise FileNotFoundError(
            f"No milestone files found in '{directory}'. "
            "Add documentation or override the directory."
        )
    return sorted(phases, key=lambda phase: phase.number)


def find_phase(phases: Iterable[Phase], number: int) -> Phase:
    """Return the phase with the given number."""

    for phase in phases:
        if phase.number == number:
            return phase
    raise ValueError(f"Unknown phase number: {number}")


def next_phase(phases: Sequence[Phase], after: int | None = None) -> Phase:
    """Return the next phase after the provided number.

    If ``after`` is ``None`` the first phase is returned. Phases are evaluated in
    numerical order regardless of the sequence ordering, so callers can pass any
    iterable without having to pre-sort it.
    """

    ordered = sorted(phases, key=lambda phase: phase.number)
    if after is None:
        return ordered[0]

    for phase in ordered:
        if phase.number > after:
            return phase
    raise ValueError(f"No phase found after number: {after}")
