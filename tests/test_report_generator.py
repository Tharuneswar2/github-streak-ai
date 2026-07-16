"""Tests for the ReportGenerator module."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from config.settings import Settings
from scripts.ai_client import AIResponse, NvidiaAIClient
from scripts.report_generator import ReportGenerator


class TestWeeklyReport:
    """Tests for weekly report generation."""

    def test_generate_weekly_report_creates_file(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Weekly report should create a file in reports/."""
        mock_client = MagicMock(spec=NvidiaAIClient)
        mock_client.generate_weekly_analysis.return_value = AIResponse(
            content="## Weekly Analysis\n\nGood progress this week.",
            model="test",
            usage={"total_tokens": 100},
        )

        generator = ReportGenerator(
            settings=settings, ai_client=mock_client
        )
        today = date.today()
        week_num = today.isocalendar()[1]
        path = generator.generate_weekly_report(week_number=week_num, year=today.year)

        assert path.exists()
        assert path.suffix == ".md"
        assert "week-" in path.name

    def test_weekly_report_contains_stats(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Weekly report should include statistics."""
        mock_client = MagicMock(spec=NvidiaAIClient)
        mock_client.generate_weekly_analysis.return_value = AIResponse(
            content="Analysis text", model="test"
        )

        generator = ReportGenerator(settings=settings, ai_client=mock_client)
        today = date.today()
        path = generator.generate_weekly_report(
            week_number=today.isocalendar()[1], year=today.year
        )
        content = path.read_text(encoding="utf-8")
        assert "Active Days" in content or "active_days" in content.lower()

    def test_weekly_report_without_api_key(
        self, settings_no_api_key: Settings, populated_logs: list[date]
    ) -> None:
        """Should generate report without AI analysis when key is missing."""
        generator = ReportGenerator(settings=settings_no_api_key)
        today = date.today()
        path = generator.generate_weekly_report(
            week_number=today.isocalendar()[1], year=today.year
        )
        assert path.exists()


class TestMonthlyReport:
    """Tests for monthly report generation."""

    def test_generate_monthly_report_creates_file(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Monthly report should create a file in reports/."""
        mock_client = MagicMock(spec=NvidiaAIClient)
        mock_client.generate_monthly_insights.return_value = AIResponse(
            content="## Monthly Insights\n\nStrong growth observed.",
            model="test",
        )

        generator = ReportGenerator(settings=settings, ai_client=mock_client)
        today = date.today()
        path = generator.generate_monthly_report(year=today.year, month=today.month)

        assert path.exists()
        assert "month-" in path.name

    def test_monthly_report_correct_filename(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Monthly report filename should match pattern month-YYYY-MM.md."""
        mock_client = MagicMock(spec=NvidiaAIClient)
        mock_client.generate_monthly_insights.return_value = AIResponse(
            content="Insights", model="test"
        )

        generator = ReportGenerator(settings=settings, ai_client=mock_client)
        path = generator.generate_monthly_report(year=2024, month=6)
        assert path.name == "month-2024-06.md"


class TestWeekDateRange:
    """Tests for week date range calculation."""

    def test_week_1_starts_correctly(self) -> None:
        """Week 1 should start on the correct Monday."""
        start, end = ReportGenerator._get_week_date_range(1, 2024)
        assert start.weekday() == 0  # Monday
        assert end.weekday() == 6    # Sunday
        assert (end - start).days == 6

    def test_week_range_is_7_days(self) -> None:
        """Week range should always be exactly 7 days."""
        for week in [1, 10, 26, 52]:
            start, end = ReportGenerator._get_week_date_range(week, 2024)
            assert (end - start).days == 6
