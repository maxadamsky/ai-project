from __future__ import annotations

import subprocess
from unittest import mock

import pytest

from ai_learning_studio import cli


def test_auto_sync_skipped_without_flag():
    runner = mock.Mock()
    logger = mock.Mock()

    result = cli.auto_sync_repository(env={}, runner=runner, logger=logger)

    assert result is False
    runner.assert_not_called()
    logger.debug.assert_called_with(
        "Auto-sync skipped: %s environment variable not enabled.",
        cli.AUTO_PULL_ENV_VAR,
    )


def test_auto_sync_runs_with_flag():
    runner = mock.Mock()
    runner.side_effect = [
        mock.Mock(stdout="true\n"),
        mock.Mock(),
        mock.Mock(),
    ]

    result = cli.auto_sync_repository(
        env={cli.AUTO_PULL_ENV_VAR: "1"},
        runner=runner,
        logger=None,
    )

    assert result is True
    expected_calls = [
        mock.call(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            cwd=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ),
        mock.call(
            ["git", "fetch", "--all", "--prune"],
            check=True,
            cwd=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ),
        mock.call(
            ["git", "pull", "--ff-only"],
            check=True,
            cwd=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ),
    ]
    runner.assert_has_calls(expected_calls)


def test_auto_sync_handles_failures_gracefully():
    runner = mock.Mock()
    runner.side_effect = [
        mock.Mock(stdout="true\n"),
        subprocess.CalledProcessError(returncode=1, cmd="git fetch"),
    ]
    logger = mock.Mock()

    result = cli.auto_sync_repository(
        env={cli.AUTO_PULL_ENV_VAR: "true"},
        runner=runner,
        logger=logger,
    )

    assert result is False
    assert runner.call_count == 2
    logger.warning.assert_called()


def test_cli_main_invokes_auto_sync_before_phase(monkeypatch):
    calls = []

    def fake_auto_sync_repository(**kwargs):
        calls.append("auto")
        return True

    def fake_load_phase(name, logger):
        calls.append("load")
        return cli.PhaseResult(name=name, status="ok")

    monkeypatch.setattr(cli, "auto_sync_repository", fake_auto_sync_repository)
    monkeypatch.setattr(cli, "_load_phase", fake_load_phase)

    result = cli.main(["--phase", "plan"])

    assert result.status == "ok"
    assert calls == ["auto", "load"]
