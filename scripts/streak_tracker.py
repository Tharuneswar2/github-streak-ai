"""Streak tracking for contribution consistency.

Calculates current and longest streaks based on daily log files,
providing status indicators and streak metadata.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from config.constants import STREAK_ACTIVE, STREAK_AT_RISK, STREAK_BROKEN
from config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class StreakTracker:
    """Tracks daily contribution streaks based on log file existence.

    A streak is a consecutive sequence of days where a log file exists.
    The streak can be 'active' (today has a log), 'at risk' (yesterday
    had a log but today doesn't yet), or 'broken' (gap > 1 day).

    Example:
        >>> tracker = StreakTracker()
        >>> info = tracker.get_streak_info()
        >>> print(f"Current: {info['current_streak']} days {info['status']}")
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the streak tracker.

        Args:
            settings: Application settings. If None, loads from environment.
        """
        self._settings = settings or get_settings()
        self._logs_dir = self._settings.logs_dir

    def _get_log_dates(self) -> list[date]:
        """Scan the logs directory for all dates with log files.

        Returns:
            Sorted list of dates.
        """
        from datetime import datetime as dt

        dates: list[date] = []
        if not self._logs_dir.exists():
            return dates

        for md_file in self._logs_dir.rglob("*.md"):
            try:
                parsed = dt.strptime(md_file.stem, "%Y-%m-%d").date()
                dates.append(parsed)
            except ValueError:
                continue
        return sorted(dates)

    def get_current_streak(self) -> int:
        """Calculate the current consecutive-day log streak.

        A streak counts backward from today (or yesterday if today's log
        isn't written yet) through each consecutive day with a log.

        Returns:
            Number of consecutive days in the current streak.
        """
        log_dates = self._get_log_dates()
        if not log_dates:
            return 0

        today = date.today()
        log_set = set(log_dates)

        # Check if today or yesterday has a log
        check_date = today
        if today not in log_set:
            yesterday = today - timedelta(days=1)
            if yesterday not in log_set:
                return 0
            check_date = yesterday

        streak = 0
        while check_date in log_set:
            streak += 1
            check_date -= timedelta(days=1)

        return streak

    def get_longest_streak(self) -> int:
        """Calculate the longest consecutive-day log streak ever.

        Returns:
            Length of the longest streak in days.
        """
        log_dates = self._get_log_dates()
        if not log_dates:
            return 0

        longest = 1
        current = 1

        for i in range(1, len(log_dates)):
            if log_dates[i] - log_dates[i - 1] == timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest

    def get_status(self) -> str:
        """Get the current streak status indicator.

        Returns:
            One of STREAK_ACTIVE, STREAK_AT_RISK, or STREAK_BROKEN.
        """
        log_dates = self._get_log_dates()
        if not log_dates:
            return STREAK_BROKEN

        today = date.today()
        log_set = set(log_dates)

        if today in log_set:
            return STREAK_ACTIVE

        yesterday = today - timedelta(days=1)
        if yesterday in log_set:
            return STREAK_AT_RISK

        return STREAK_BROKEN

    def get_total_logged_days(self) -> int:
        """Get the total number of days with logs.

        Returns:
            Total log count.
        """
        return len(self._get_log_dates())

    def get_streak_info(self) -> dict[str, Any]:
        """Get comprehensive streak information.

        Returns:
            Dictionary with current_streak, longest_streak, status,
            total_logged_days, and today_logged.
        """
        log_dates = self._get_log_dates()
        today = date.today()
        log_set = set(log_dates)

        return {
            "current_streak": self.get_current_streak(),
            "longest_streak": self.get_longest_streak(),
            "status": self.get_status(),
            "total_logged_days": len(log_dates),
            "today_logged": today in log_set,
            "first_log": log_dates[0].isoformat() if log_dates else None,
            "last_log": log_dates[-1].isoformat() if log_dates else None,
        }

    def get_activity_calendar(self, year: int | None = None, month: int | None = None) -> dict[str, bool]:
        """Generate an activity calendar showing which days have logs.

        Args:
            year: Year to show. Defaults to current year.
            month: Month to show. If None, shows the full year.

        Returns:
            Dictionary mapping date strings (YYYY-MM-DD) to bool (has log).
        """
        today = date.today()
        year = year or today.year

        log_set = set(self._get_log_dates())

        if month is not None:
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(year, month + 1, 1) - timedelta(days=1)
        else:
            start = date(year, 1, 1)
            end = date(year, 12, 31)

        calendar: dict[str, bool] = {}
        current = start
        while current <= end:
            calendar[current.isoformat()] = current in log_set
            current += timedelta(days=1)

        return calendar
