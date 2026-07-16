"""Tests for the StreakTracker module."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from config.constants import STREAK_ACTIVE, STREAK_AT_RISK, STREAK_BROKEN
from config.settings import Settings
from scripts.streak_tracker import StreakTracker


class TestCurrentStreak:
    """Tests for current streak calculation."""

    def test_current_streak_with_consecutive_days(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Should detect a streak from consecutive log days."""
        tracker = StreakTracker(settings)
        streak = tracker.get_current_streak()
        assert streak >= 1

    def test_current_streak_empty_logs(self, settings: Settings) -> None:
        """Should return 0 when no logs exist."""
        tracker = StreakTracker(settings)
        assert tracker.get_current_streak() == 0

    def test_current_streak_gap_breaks_streak(
        self, settings: Settings, tmp_project: Path
    ) -> None:
        """A gap of 2+ days should break the streak."""
        tracker = StreakTracker(settings)
        today = date.today()

        # Create a log from 5 days ago only
        old_date = today - timedelta(days=5)
        log_dir = tmp_project / "logs" / str(old_date.year) / f"{old_date.month:02d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"{old_date.isoformat()}.md").write_text("# Old log\n")

        assert tracker.get_current_streak() == 0


class TestLongestStreak:
    """Tests for longest streak calculation."""

    def test_longest_streak_with_data(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Should calculate the longest consecutive sequence."""
        tracker = StreakTracker(settings)
        longest = tracker.get_longest_streak()
        assert longest >= 1

    def test_longest_streak_empty(self, settings: Settings) -> None:
        """Should return 0 when no logs exist."""
        tracker = StreakTracker(settings)
        assert tracker.get_longest_streak() == 0

    def test_longest_streak_single_day(
        self, settings: Settings, tmp_project: Path
    ) -> None:
        """A single log day should give a streak of 1."""
        today = date.today()
        log_dir = tmp_project / "logs" / str(today.year) / f"{today.month:02d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"{today.isoformat()}.md").write_text("# Log\n")

        tracker = StreakTracker(settings)
        assert tracker.get_longest_streak() == 1


class TestStreakStatus:
    """Tests for streak status indicators."""

    def test_status_active_today(
        self, settings: Settings, tmp_project: Path
    ) -> None:
        """Status should be ACTIVE if today has a log."""
        today = date.today()
        log_dir = tmp_project / "logs" / str(today.year) / f"{today.month:02d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"{today.isoformat()}.md").write_text("# Log\n")

        tracker = StreakTracker(settings)
        assert tracker.get_status() == STREAK_ACTIVE

    def test_status_at_risk(
        self, settings: Settings, tmp_project: Path
    ) -> None:
        """Status should be AT_RISK if yesterday has a log but not today."""
        yesterday = date.today() - timedelta(days=1)
        log_dir = tmp_project / "logs" / str(yesterday.year) / f"{yesterday.month:02d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / f"{yesterday.isoformat()}.md").write_text("# Log\n")

        tracker = StreakTracker(settings)
        assert tracker.get_status() == STREAK_AT_RISK

    def test_status_broken(self, settings: Settings) -> None:
        """Status should be BROKEN when no recent logs."""
        tracker = StreakTracker(settings)
        assert tracker.get_status() == STREAK_BROKEN


class TestStreakInfo:
    """Tests for comprehensive streak info."""

    def test_streak_info_has_all_keys(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """get_streak_info should return all expected keys."""
        tracker = StreakTracker(settings)
        info = tracker.get_streak_info()
        expected_keys = {
            "current_streak", "longest_streak", "status",
            "total_logged_days", "today_logged", "first_log", "last_log",
        }
        assert set(info.keys()) == expected_keys

    def test_total_logged_days(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """total_logged_days should match number of log files."""
        tracker = StreakTracker(settings)
        assert tracker.get_total_logged_days() == len(populated_logs)


class TestActivityCalendar:
    """Tests for activity calendar generation."""

    def test_activity_calendar_current_month(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Calendar should include entries for every day of the month."""
        tracker = StreakTracker(settings)
        today = date.today()
        calendar = tracker.get_activity_calendar(today.year, today.month)
        assert len(calendar) >= 28  # At least 28 days in any month
        assert all(isinstance(v, bool) for v in calendar.values())
