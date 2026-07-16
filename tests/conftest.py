"""Shared pytest fixtures for GitHub Streak AI tests.

Provides temporary directories, mock settings, mock AI clients,
and pre-populated log structures for test isolation.
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from config.settings import Settings


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with required subdirectories.

    Returns:
        Path to the temporary project root.
    """
    for subdir in ("logs", "reports", "templates", "dashboard"):
        (tmp_path / subdir).mkdir()
    return tmp_path


@pytest.fixture
def settings(tmp_project: Path) -> Settings:
    """Create a Settings instance pointing at the temporary project.

    Returns:
        Settings with project_root set to tmp_project.
    """
    return Settings(
        nvidia_api_key="test-api-key-12345",
        model="test-model",
        nvidia_base_url="https://test.api.nvidia.com/v1",
        project_root=tmp_project,
    )


@pytest.fixture
def settings_no_api_key(tmp_project: Path) -> Settings:
    """Create a Settings instance without an API key.

    Returns:
        Settings with empty nvidia_api_key.
    """
    return Settings(
        nvidia_api_key="",
        model="test-model",
        nvidia_base_url="https://test.api.nvidia.com/v1",
        project_root=tmp_project,
    )


@pytest.fixture
def mock_ai_response() -> dict[str, Any]:
    """Standard mock API response payload.

    Returns:
        Dict matching the NVIDIA NIM response format.
    """
    return {
        "id": "test-id",
        "object": "chat.completion",
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "## AI Summary\n\nThis is a test summary.\n\n- Key takeaway 1\n- Key takeaway 2\n\n### Action Items\n- Follow up on testing",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }


@pytest.fixture
def populated_logs(tmp_project: Path) -> list[date]:
    """Create a set of sample log files spanning multiple days.

    Creates logs for the last 7 days with realistic content.

    Returns:
        List of dates that have logs.
    """
    dates: list[date] = []
    today = date.today()

    for i in range(7):
        d = today - timedelta(days=i)
        log_dir = tmp_project / "logs" / str(d.year) / f"{d.month:02d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{d.isoformat()}.md"
        log_file.write_text(
            f"# Daily Log — {d.isoformat()}\n\n"
            f"**Date:** {d.isoformat()}\n\n"
            "## Goals\n\n- Learn Python testing\n- Review PRs\n\n---\n\n"
            "## Completed Tasks\n\n- Wrote unit tests\n- Code review\n\n---\n\n"
            "## Study Notes\n\n- Python pytest fixtures\n\n---\n\n"
            "## Coding Notes\n\n- Used dataclasses for models\n\n---\n\n"
            "## Bugs Fixed\n\n- Fixed import error\n\n---\n\n"
            "## Learnings\n\n- Learned about mocking\n\n---\n\n"
            "## Tomorrow Plan\n\n- Continue testing\n\n---\n\n"
            "## AI Summary\n\n- Pending\n\n---\n",
            encoding="utf-8",
        )
        dates.append(d)

    return sorted(dates)


@pytest.fixture
def mock_git_repo(tmp_project: Path) -> MagicMock:
    """Create a mock git.Repo object.

    Returns:
        MagicMock configured as a git.Repo.
    """
    mock_repo = MagicMock()
    mock_repo.working_dir = str(tmp_project)
    mock_repo.git.rev_list.return_value = "42"
    mock_repo.git.ls_files.return_value = "cli.py\nconfig/settings.py\nREADME.md"
    mock_repo.git.log.return_value = ""
    mock_repo.git.shortlog.return_value = "  10\tTest Author"
    mock_repo.git.diff.return_value = ""
    return mock_repo


@pytest.fixture
def copy_templates(tmp_project: Path) -> None:
    """Copy Jinja2 templates to the temporary project's templates dir."""
    src_templates = Path(__file__).parent.parent / "templates"
    dst_templates = tmp_project / "templates"
    if src_templates.exists():
        for template_file in src_templates.glob("*.j2"):
            (dst_templates / template_file.name).write_text(
                template_file.read_text(encoding="utf-8"), encoding="utf-8"
            )
