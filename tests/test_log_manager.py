"""Tests for the LogManager module."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from config.settings import Settings
from scripts.log_manager import LogManager, LogNotFoundError, LogCorruptedError


class TestLogCreation:
    """Tests for creating daily log files."""

    def test_create_daily_log_creates_file(self, settings: Settings) -> None:
        """A new log file should be created for today."""
        manager = LogManager(settings)
        today = date.today()
        path = manager.create_daily_log(today)
        assert path.exists()
        assert path.suffix == ".md"

    def test_create_daily_log_correct_path(self, settings: Settings) -> None:
        """Log file should be at logs/YYYY/MM/YYYY-MM-DD.md."""
        manager = LogManager(settings)
        target = date(2024, 3, 15)
        path = manager.create_daily_log(target)
        expected = settings.logs_dir / "2024" / "03" / "2024-03-15.md"
        assert path == expected

    def test_create_daily_log_has_content(self, settings: Settings) -> None:
        """Created log should contain the expected sections."""
        manager = LogManager(settings)
        path = manager.create_daily_log(date(2024, 6, 1))
        content = path.read_text(encoding="utf-8")
        assert "Goals" in content
        assert "Completed Tasks" in content
        assert "Study Notes" in content
        assert "AI Summary" in content

    def test_create_daily_log_idempotent(self, settings: Settings) -> None:
        """Creating the same log twice should not overwrite existing content."""
        manager = LogManager(settings)
        target = date(2024, 1, 10)
        path1 = manager.create_daily_log(target)
        path1.write_text("custom content", encoding="utf-8")
        path2 = manager.create_daily_log(target)
        assert path1 == path2
        assert path2.read_text(encoding="utf-8") == "custom content"

    def test_create_daily_log_with_template(
        self, settings: Settings, copy_templates: None
    ) -> None:
        """Log should use Jinja2 template when available."""
        manager = LogManager(settings)
        path = manager.create_daily_log(date(2024, 5, 20))
        content = path.read_text(encoding="utf-8")
        assert "Daily Log" in content


class TestLogReading:
    """Tests for reading log files."""

    def test_get_log_returns_content(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Should return the content of an existing log."""
        manager = LogManager(settings)
        content = manager.get_log(populated_logs[0])
        assert "Daily Log" in content

    def test_get_log_raises_not_found(self, settings: Settings) -> None:
        """Should raise LogNotFoundError for missing dates."""
        manager = LogManager(settings)
        with pytest.raises(LogNotFoundError):
            manager.get_log(date(2020, 1, 1))

    def test_log_exists_true(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """log_exists should return True for dates with logs."""
        manager = LogManager(settings)
        assert manager.log_exists(populated_logs[0]) is True

    def test_log_exists_false(self, settings: Settings) -> None:
        """log_exists should return False for dates without logs."""
        manager = LogManager(settings)
        assert manager.log_exists(date(2020, 1, 1)) is False


class TestLogListing:
    """Tests for listing and querying logs."""

    def test_list_logs_returns_all(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """list_logs should return all log file paths."""
        manager = LogManager(settings)
        logs = manager.list_logs()
        assert len(logs) == len(populated_logs)

    def test_get_log_dates(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """get_log_dates should return sorted date list."""
        manager = LogManager(settings)
        dates = manager.get_log_dates()
        assert dates == sorted(populated_logs)

    def test_get_logs_for_range(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Should return logs within the specified date range."""
        manager = LogManager(settings)
        start = populated_logs[0]
        end = populated_logs[2]
        results = manager.get_logs_for_range(start, end)
        assert len(results) >= 1
        for d, content in results:
            assert start <= d <= end

    def test_get_total_log_count(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Should return correct total count."""
        manager = LogManager(settings)
        assert manager.get_total_log_count() == len(populated_logs)


class TestLogUpdating:
    """Tests for updating log content."""

    def test_update_log_writes_content(self, settings: Settings) -> None:
        """update_log should write the given content."""
        manager = LogManager(settings)
        target = date(2024, 7, 1)
        manager.update_log(target, "# Updated Content\n")
        content = manager.get_log(target)
        assert content == "# Updated Content\n"

    def test_update_section(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """update_section should replace the specified section."""
        manager = LogManager(settings)
        target = populated_logs[0]
        manager.update_section(target, "AI Summary", "This is the AI summary.")
        content = manager.get_log(target)
        assert "This is the AI summary." in content
