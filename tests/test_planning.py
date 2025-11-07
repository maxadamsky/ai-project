"""Smoke tests for the planning utilities."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_learning_studio import default_phases, next_phase
from ai_learning_studio.cli import (
    render_next_phase,
    render_phase_details,
    render_phase_summary,
)

_ENV_VAR = "AI_LEARNING_STUDIO_MILESTONES_DIR"


def _write_milestone(directory: Path, name: str, body: str) -> None:
    (directory / name).write_text(body, encoding="utf-8")


class PlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

        milestone_dir = Path(self.tempdir.name)
        _write_milestone(
            milestone_dir,
            "00_start.md",
            """# Milestone 00 – Start

## Objective
Lay the groundwork for the learning studio and document the initial environment.

## Checklist
- Bootstrap the repository tooling.
- Capture baseline journal entries.
""",
        )
        _write_milestone(
            milestone_dir,
            "01_follow_up.md",
            """# Milestone 01 – Follow Up

## Objective
Build upon the foundation by experimenting with lightweight language models.

## Checklist
1. Launch a local inference runtime.
2. Record prompt and sampling observations.
""",
        )

        self.previous_env = os.environ.get(_ENV_VAR)
        os.environ[_ENV_VAR] = self.tempdir.name

    def tearDown(self) -> None:
        if self.previous_env is None:
            os.environ.pop(_ENV_VAR, None)
        else:
            os.environ[_ENV_VAR] = self.previous_env

    def test_default_phases_cover_expected_range(self) -> None:
        phases = default_phases()
        numbers = {phase.number for phase in phases}
        self.assertEqual(len(phases), 2)
        self.assertSetEqual(numbers, {0, 1})

    def test_render_phase_summary_includes_all_phases(self) -> None:
        summary = render_phase_summary()
        self.assertIn("Phase 0", summary)
        self.assertIn("Phase 1", summary)
        self.assertIn("Start", summary)

    def test_render_phase_details_mentions_focus(self) -> None:
        details = render_phase_details(1)
        self.assertIn("Follow Up", details)
        self.assertIn("Focus:", details)
        self.assertIn("language models", details)

    def test_next_phase_progression(self) -> None:
        phases = default_phases()
        first = next_phase(phases)
        self.assertEqual(first.number, 0)

        second = next_phase(phases, after=0)
        self.assertEqual(second.number, 1)

    def test_render_next_phase_context(self) -> None:
        summary = render_next_phase(after=0)
        self.assertIn("Next step after completing Phase 0", summary)
        self.assertIn("Phase 1", summary)


if __name__ == "__main__":
    unittest.main()
