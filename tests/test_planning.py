"""Smoke tests for the planning utilities."""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ai_learning_studio import default_phases, next_phase
from ai_learning_studio.cli import (
    AUTO_SYNC_ENV_VAR,
    maybe_auto_sync_repository,
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

        self.previous_auto_sync_env = os.environ.get(AUTO_SYNC_ENV_VAR)
        os.environ.pop(AUTO_SYNC_ENV_VAR, None)

    def tearDown(self) -> None:
        if self.previous_env is None:
            os.environ.pop(_ENV_VAR, None)
        else:
            os.environ[_ENV_VAR] = self.previous_env

        if self.previous_auto_sync_env is None:
            os.environ.pop(AUTO_SYNC_ENV_VAR, None)
        else:
            os.environ[AUTO_SYNC_ENV_VAR] = self.previous_auto_sync_env

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

    def test_auto_sync_skipped_without_env_flag(self) -> None:
        with mock.patch("ai_learning_studio.cli._run_git_command") as mocked_run:
            maybe_auto_sync_repository(repo_path=Path.cwd())
        mocked_run.assert_not_called()

    def test_auto_sync_runs_git_commands_when_enabled(self) -> None:
        os.environ[AUTO_SYNC_ENV_VAR] = "1"

        def _mock_run(args, cwd):
            if args[0] == "rev-parse":
                return subprocess.CompletedProcess(args, 0, stdout="true\n", stderr="")
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

        with mock.patch("ai_learning_studio.cli._run_git_command", side_effect=_mock_run) as mocked_run:
            maybe_auto_sync_repository(repo_path=Path.cwd())

        self.assertGreaterEqual(mocked_run.call_count, 3)
        mocked_run.assert_any_call(["rev-parse", "--is-inside-work-tree"], cwd=Path.cwd())
        mocked_run.assert_any_call(["fetch", "--all"], cwd=Path.cwd())
        mocked_run.assert_any_call(["pull"], cwd=Path.cwd())

    def test_auto_sync_handles_git_errors_gracefully(self) -> None:
        os.environ[AUTO_SYNC_ENV_VAR] = "yes"

        def _mock_run(args, cwd):
            if args[0] == "rev-parse":
                return subprocess.CompletedProcess(args, 0, stdout="true\n", stderr="")
            raise subprocess.CalledProcessError(1, ["git", *args], stderr="remote rejected")

        stderr_buffer = io.StringIO()
        with mock.patch("ai_learning_studio.cli._run_git_command", side_effect=_mock_run):
            with contextlib.redirect_stderr(stderr_buffer):
                maybe_auto_sync_repository(repo_path=Path.cwd())

        self.assertIn("Git command failed", stderr_buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
