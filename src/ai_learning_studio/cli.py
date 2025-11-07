"""Command line interface for AI Learning Studio."""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Sequence

AUTO_PULL_ENV_VAR = "AI_LEARNING_STUDIO_AUTO_PULL"


@dataclass
class PhaseResult:
    """Lightweight representation of a planning phase result."""

    name: str
    status: str


def _create_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    description = (
        "Run AI Learning Studio planning phases. "
        "Set the AI_LEARNING_STUDIO_AUTO_PULL environment variable to automatically "
        "fetch and pull Git updates before planning."
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--phase",
        default="plan",
        help="Planning phase to execute (default: plan).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging for troubleshooting.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="AI Learning Studio 0.1.0",
    )
    return parser


def _configure_logging(verbose: bool) -> logging.Logger:
    """Create a logger respecting the verbosity flag."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level)
    return logging.getLogger("ai_learning_studio")


def auto_sync_repository(
    *,
    env: Optional[Mapping[str, str]] = None,
    runner=subprocess.run,
    cwd: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """Synchronise the local Git repository when the opt-in flag is enabled.

    Parameters
    ----------
    env:
        Optional mapping that overrides :data:`os.environ` for reading the
        opt-in flag. When omitted the current process environment is used.
    runner:
        Callable compatible with :func:`subprocess.run`, used to allow
        dependency injection for tests.
    cwd:
        Working directory for Git commands. Defaults to ``None`` which
        inherits the current process working directory.
    logger:
        Logger instance for emitting debug information.

    Returns
    -------
    bool
        ``True`` when synchronisation commands executed successfully, ``False``
        otherwise.
    """

    env = env or os.environ
    opt_in = env.get(AUTO_PULL_ENV_VAR)
    if not _is_truthy(opt_in):
        if logger:
            logger.debug(
                "Auto-sync skipped: %s environment variable not enabled.",
                AUTO_PULL_ENV_VAR,
            )
        return False

    if not _is_git_repository(runner=runner, cwd=cwd, logger=logger):
        return False

    commands: Iterable[Sequence[str]] = (
        ["git", "fetch", "--all", "--prune"],
        ["git", "pull", "--ff-only"],
    )

    success = True
    for command in commands:
        try:
            runner(
                command,
                check=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if logger:
                logger.debug("Command succeeded: %s", " ".join(command))
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            success = False
            if logger:
                logger.warning("Git auto-sync failed for '%s': %s", " ".join(command), exc)
            break

    return success


def _is_git_repository(
    *,
    runner,
    cwd: Optional[str],
    logger: Optional[logging.Logger],
) -> bool:
    """Return ``True`` when the current working directory is part of a Git repository."""
    try:
        result = runner(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        if logger:
            logger.debug("Git repository check failed: %s", exc)
        return False

    is_inside = str(result.stdout).strip().lower() == "true"
    if logger:
        logger.debug("Inside git repository: %s", is_inside)
    return is_inside


def _is_truthy(value: Optional[str]) -> bool:
    """Normalise textual truthy values."""
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _load_phase(name: str, logger: logging.Logger) -> PhaseResult:
    """Placeholder for the actual planning phase loader."""
    logger.info("Executing planning phase: %s", name)
    return PhaseResult(name=name, status="completed")


def main(argv: Optional[Sequence[str]] = None) -> PhaseResult:
    """Entrypoint executed by the ``ai-learning-studio`` console script."""
    parser = _create_parser()
    args = parser.parse_args(argv)
    logger = _configure_logging(args.verbose)

    auto_sync_repository(logger=logger)

    result = _load_phase(args.phase, logger)
    return result


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
