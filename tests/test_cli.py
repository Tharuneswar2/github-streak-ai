"""Tests for the CLI module."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from cli import app
from config.settings import Settings


runner = CliRunner()


class TestNewCommand:
    """Tests for the 'new' CLI command."""

    def test_new_creates_log(self, settings: Settings) -> None:
        """'new' should create a log file for today."""
        with patch("cli.get_settings", return_value=settings):
            result = runner.invoke(app, ["new"])
        assert result.exit_code == 0
        assert "Created" in result.output or "Existing" in result.output

    def test_new_with_date(self, settings: Settings) -> None:
        """'new' with a date argument should create log for that date."""
        with patch("cli.get_settings", return_value=settings):
            result = runner.invoke(app, ["new", "2024-06-15"])
        assert result.exit_code == 0

    def test_new_invalid_date(self, settings: Settings) -> None:
        """'new' with invalid date should show error."""
        with patch("cli.get_settings", return_value=settings):
            result = runner.invoke(app, ["new", "not-a-date"])
        assert result.exit_code == 1


class TestSummaryCommand:
    """Tests for the 'summary' CLI command."""

    def test_summary_no_log_shows_error(self, settings: Settings) -> None:
        """'summary' should error when no log exists."""
        with patch("cli.get_settings", return_value=settings):
            result = runner.invoke(app, ["summary"])
        assert result.exit_code == 1
        assert "Not Found" in result.output or "not" in result.output.lower()

    def test_summary_no_api_key(
        self, settings_no_api_key: Settings, populated_logs: list[date]
    ) -> None:
        """'summary' without API key should show warning."""
        with patch("cli.get_settings", return_value=settings_no_api_key):
            result = runner.invoke(app, ["summary"])
        assert result.exit_code == 1


class TestStatsCommand:
    """Tests for the 'stats' CLI command."""

    def test_stats_shows_streak_info(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """'stats' should display streak statistics."""
        with patch("cli.get_settings", return_value=settings):
            result = runner.invoke(app, ["stats"])
        assert result.exit_code == 0
        assert "Streak" in result.output


class TestHelpCommand:
    """Tests for the 'help' CLI command."""

    def test_help_shows_commands(self, settings: Settings) -> None:
        """'help' should list all available commands."""
        result = runner.invoke(app, ["help"])
        assert result.exit_code == 0
        assert "new" in result.output.lower()
        assert "summary" in result.output.lower()
        assert "weekly" in result.output.lower()


class TestDashboardCommand:
    """Tests for the 'dashboard' CLI command."""

    def test_dashboard_generates(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """'dashboard' should generate README.md."""
        with patch("cli.get_settings", return_value=settings):
            result = runner.invoke(app, ["dashboard"])
        assert result.exit_code == 0
        assert "Dashboard" in result.output or "dashboard" in result.output.lower()
