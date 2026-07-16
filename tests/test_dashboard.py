"""Tests for the DashboardGenerator module."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from config.settings import Settings
from dashboard.badges import BadgeGenerator
from dashboard.generator import DashboardGenerator


class TestBadgeGenerator:
    """Tests for shields.io badge generation."""

    def test_streak_badge_format(self) -> None:
        """Streak badge should be valid markdown image."""
        gen = BadgeGenerator()
        badge = gen.streak_badge(42)
        assert badge.startswith("![")
        assert "img.shields.io" in badge
        assert "42" in badge

    def test_logs_badge(self) -> None:
        """Logs badge should include the count."""
        gen = BadgeGenerator()
        badge = gen.logs_badge(100)
        assert "100" in badge

    def test_all_badges(self) -> None:
        """generate_all_badges should return multiple badges."""
        gen = BadgeGenerator()
        result = gen.generate_all_badges(
            streak=10, logs=50, commits=200, hours=15.5, projects=3
        )
        assert result.count("![") == 5  # 5 badges

    def test_tech_badge(self) -> None:
        """Tech badge should include the technology name."""
        gen = BadgeGenerator()
        badge = gen.tech_badge("Python")
        assert "Python" in badge

    def test_custom_badge(self) -> None:
        """Custom badge should accept arbitrary label and value."""
        gen = BadgeGenerator()
        badge = gen.custom_badge("Status", "Active", "green")
        assert "Status" in badge
        assert "Active" in badge


class TestDashboardGenerator:
    """Tests for README dashboard generation."""

    def test_generate_creates_readme(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """generate() should create a README.md file."""
        gen = DashboardGenerator(settings)
        path = gen.generate()
        assert path.exists()
        assert path.name == "README.md"

    def test_dashboard_contains_streak_info(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Dashboard should display streak information."""
        gen = DashboardGenerator(settings)
        path = gen.generate()
        content = path.read_text(encoding="utf-8")
        assert "Current Streak" in content
        assert "Longest Streak" in content

    def test_dashboard_contains_badges(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Dashboard should include shields.io badges."""
        gen = DashboardGenerator(settings)
        path = gen.generate()
        content = path.read_text(encoding="utf-8")
        assert "img.shields.io" in content

    def test_dashboard_contains_progress(
        self, settings: Settings, populated_logs: list[date]
    ) -> None:
        """Dashboard should include progress bars."""
        gen = DashboardGenerator(settings)
        path = gen.generate()
        content = path.read_text(encoding="utf-8")
        assert "Progress" in content

    def test_dashboard_custom_output_path(
        self, settings: Settings, populated_logs: list[date], tmp_path: Path
    ) -> None:
        """generate() should support custom output path."""
        gen = DashboardGenerator(settings)
        custom_path = tmp_path / "custom_dashboard.md"
        result = gen.generate(output_path=custom_path)
        assert result == custom_path
        assert custom_path.exists()

    def test_progress_bar(self) -> None:
        """Progress bar should show correct percentage."""
        bar = DashboardGenerator._progress_bar(50, 100)
        assert "50%" in bar

    def test_progress_bar_zero(self) -> None:
        """Progress bar with 0 maximum should show 0%."""
        bar = DashboardGenerator._progress_bar(0, 0)
        assert "0%" in bar

    def test_progress_bar_full(self) -> None:
        """Progress bar at 100% should show full."""
        bar = DashboardGenerator._progress_bar(100, 100)
        assert "100%" in bar
