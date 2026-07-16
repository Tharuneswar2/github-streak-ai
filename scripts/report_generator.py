"""Report generation for weekly and monthly summaries.

Aggregates daily log data, computes statistics, and generates
professional markdown reports using Jinja2 templates and AI insights.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from config.constants import (
    DATE_FORMAT,
    MONTHLY_REPORT_PATTERN,
    MONTHLY_REPORT_TEMPLATE,
    WEEKLY_REPORT_PATTERN,
    WEEKLY_REPORT_TEMPLATE,
)
from config.settings import Settings, get_settings
from scripts.ai_client import AIClientError, NvidiaAIClient
from scripts.log_manager import LogManager
from scripts.streak_tracker import StreakTracker

logger = logging.getLogger(__name__)


class ReportError(Exception):
    """Base exception for report generation errors."""


class ReportGenerator:
    """Generates weekly and monthly reports from daily log data.

    Aggregates logs, calculates statistics, and optionally enriches
    reports with AI-powered analysis via the NVIDIA NIM API.

    Example:
        >>> generator = ReportGenerator()
        >>> path = generator.generate_weekly_report(week_number=28, year=2024)
        >>> print(f"Report saved to: {path}")
    """

    def __init__(
        self,
        settings: Settings | None = None,
        log_manager: LogManager | None = None,
        ai_client: NvidiaAIClient | None = None,
        streak_tracker: StreakTracker | None = None,
    ) -> None:
        """Initialize the ReportGenerator.

        Args:
            settings: Application settings. If None, loads from environment.
            log_manager: LogManager instance for reading logs.
            ai_client: NvidiaAIClient instance for AI analysis.
            streak_tracker: StreakTracker instance for streak data.
        """
        self._settings = settings or get_settings()
        self._log_manager = log_manager or LogManager(self._settings)
        self._ai_client = ai_client or NvidiaAIClient(self._settings)
        self._streak_tracker = streak_tracker or StreakTracker(self._settings)
        self._reports_dir = self._settings.reports_dir
        self._reports_dir.mkdir(parents=True, exist_ok=True)

        # Jinja2 environment
        templates_dir = self._settings.templates_dir
        if templates_dir.exists():
            self._jinja_env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                keep_trailing_newline=True,
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            self._jinja_env = None
            logger.warning("Templates directory not found at %s", templates_dir)

    @staticmethod
    def _get_week_date_range(week_number: int, year: int) -> tuple[date, date]:
        """Calculate the start (Monday) and end (Sunday) dates for a given ISO week.

        Args:
            week_number: ISO week number (1-53).
            year: Year.

        Returns:
            Tuple of (start_date, end_date).
        """
        jan4 = date(year, 1, 4)
        start_of_week1 = jan4 - timedelta(days=jan4.weekday())
        week_start = start_of_week1 + timedelta(weeks=week_number - 1)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end

    def _aggregate_logs(
        self, start: date, end: date
    ) -> tuple[list[tuple[date, str]], str]:
        """Collect and concatenate logs for a date range.

        Args:
            start: Start date (inclusive).
            end: End date (inclusive).

        Returns:
            Tuple of (logs_list, concatenated_content).
        """
        logs = self._log_manager.get_logs_for_range(start, end)
        combined = "\n\n---\n\n".join(
            f"### {d.strftime(DATE_FORMAT)}\n\n{content}" for d, content in logs
        )
        return logs, combined

    def _compute_weekly_stats(
        self,
        logs: list[tuple[date, str]],
        week_start: date,
        week_end: date,
    ) -> dict[str, Any]:
        """Compute statistics for a weekly report.

        Args:
            logs: List of (date, content) tuples.
            week_start: Start of the week.
            week_end: End of the week.

        Returns:
            Dictionary of weekly statistics.
        """
        active_days = len(logs)
        total_days = (week_end - week_start).days + 1
        streak_info = self._streak_tracker.get_streak_info()

        # Count total lines and estimate study hours (rough heuristic)
        total_lines = sum(len(content.splitlines()) for _, content in logs)
        estimated_hours = round(total_lines / 50, 1)  # ~50 lines per hour of notes

        # Extract technologies mentioned (simple keyword extraction)
        technologies: set[str] = set()
        tech_keywords = [
            "python", "javascript", "typescript", "react", "node", "docker",
            "kubernetes", "aws", "gcp", "azure", "sql", "postgres", "redis",
            "git", "linux", "rust", "go", "java", "c++", "html", "css",
            "fastapi", "django", "flask", "vue", "angular", "terraform",
            "graphql", "rest", "api", "machine learning", "deep learning",
        ]
        all_content = " ".join(content.lower() for _, content in logs)
        for tech in tech_keywords:
            if tech in all_content:
                technologies.add(tech.title())

        return {
            "active_days": active_days,
            "total_days": total_days,
            "completion_rate": f"{(active_days / total_days * 100):.0f}%",
            "total_log_lines": total_lines,
            "estimated_study_hours": estimated_hours,
            "technologies_mentioned": sorted(technologies),
            "current_streak": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"],
            "streak_status": streak_info["status"],
        }

    def _render_report(
        self,
        template_name: str,
        context: dict[str, Any],
        fallback_title: str,
    ) -> str:
        """Render a report using Jinja2 or fallback to a simple format.

        Args:
            template_name: Name of the Jinja2 template.
            context: Template context dictionary.
            fallback_title: Title to use in the fallback template.

        Returns:
            Rendered markdown content.
        """
        if self._jinja_env is not None:
            try:
                template = self._jinja_env.get_template(template_name)
                return template.render(**context)
            except TemplateNotFound:
                logger.warning("Template '%s' not found, using fallback.", template_name)

        return self._fallback_report(context, fallback_title)

    @staticmethod
    def _fallback_report(context: dict[str, Any], title: str) -> str:
        """Generate a basic report when no Jinja2 template is available.

        Args:
            context: Report context dictionary.
            title: Report title.

        Returns:
            Formatted markdown string.
        """
        lines = [f"# {title}", ""]

        stats = context.get("stats", {})
        if stats:
            lines.extend(["## Statistics", ""])
            for key, value in stats.items():
                display_key = key.replace("_", " ").title()
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                lines.append(f"| {display_key} | {value} |")
            lines.extend(["", "---", ""])

        ai_analysis = context.get("ai_analysis", "")
        if ai_analysis:
            lines.extend(["## AI Analysis", "", ai_analysis, "", "---", ""])

        lines.append(
            "*Generated by [GitHub Streak AI](https://github.com/yourusername/github-streak-ai)*"
        )
        return "\n".join(lines) + "\n"

    def generate_weekly_report(
        self,
        week_number: int | None = None,
        year: int | None = None,
    ) -> Path:
        """Generate a weekly report aggregating daily logs.

        Args:
            week_number: ISO week number. Defaults to current week.
            year: Year. Defaults to current year.

        Returns:
            Path to the generated report file.
        """
        today = date.today()
        if year is None:
            year = today.year
        if week_number is None:
            week_number = today.isocalendar()[1]

        week_start, week_end = self._get_week_date_range(week_number, year)
        logs, combined_content = self._aggregate_logs(week_start, week_end)
        stats = self._compute_weekly_stats(logs, week_start, week_end)

        # Generate AI analysis if available
        ai_analysis = ""
        if self._settings.has_api_key and combined_content.strip():
            try:
                response = self._ai_client.generate_weekly_analysis(
                    combined_content, stats
                )
                ai_analysis = response.content
            except AIClientError as exc:
                logger.warning("AI analysis failed, proceeding without it: %s", exc)
                ai_analysis = f"*AI analysis unavailable: {exc}*"

        context = {
            "title": f"Weekly Report — Week {week_number}, {year}",
            "week_number": week_number,
            "year": year,
            "week_start": week_start.strftime(DATE_FORMAT),
            "week_end": week_end.strftime(DATE_FORMAT),
            "stats": stats,
            "ai_analysis": ai_analysis,
            "logs": logs,
            "generated_date": today.strftime(DATE_FORMAT),
        }

        content = self._render_report(
            WEEKLY_REPORT_TEMPLATE,
            context,
            f"Weekly Report — Week {week_number}, {year}",
        )

        filename = WEEKLY_REPORT_PATTERN.format(week=week_number)
        report_path = self._reports_dir / filename
        report_path.write_text(content, encoding="utf-8")
        logger.info("Generated weekly report: %s", report_path)
        return report_path

    def generate_monthly_report(
        self,
        year: int | None = None,
        month: int | None = None,
    ) -> Path:
        """Generate a monthly report aggregating weekly data.

        Args:
            year: Year. Defaults to current year.
            month: Month (1-12). Defaults to current month.

        Returns:
            Path to the generated report file.
        """
        today = date.today()
        if year is None:
            year = today.year
        if month is None:
            month = today.month

        # Calculate month date range
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)

        logs, combined_content = self._aggregate_logs(month_start, month_end)
        active_days = len(logs)
        total_days = (month_end - month_start).days + 1
        total_lines = sum(len(content.splitlines()) for _, content in logs)
        estimated_hours = round(total_lines / 50, 1)

        streak_info = self._streak_tracker.get_streak_info()

        stats: dict[str, Any] = {
            "active_days": active_days,
            "total_days": total_days,
            "completion_rate": f"{(active_days / total_days * 100):.0f}%",
            "estimated_study_hours": estimated_hours,
            "current_streak": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"],
            "total_log_lines": total_lines,
        }

        # Generate AI insights
        ai_insights = ""
        if self._settings.has_api_key and combined_content.strip():
            try:
                response = self._ai_client.generate_monthly_insights(
                    combined_content, stats
                )
                ai_insights = response.content
            except AIClientError as exc:
                logger.warning("AI insights failed: %s", exc)
                ai_insights = f"*AI insights unavailable: {exc}*"

        month_name = month_start.strftime("%B %Y")
        context = {
            "title": f"Monthly Report — {month_name}",
            "year": year,
            "month": month,
            "month_name": month_name,
            "month_start": month_start.strftime(DATE_FORMAT),
            "month_end": month_end.strftime(DATE_FORMAT),
            "stats": stats,
            "ai_insights": ai_insights,
            "logs": logs,
            "active_days_list": [d.strftime(DATE_FORMAT) for d, _ in logs],
            "generated_date": today.strftime(DATE_FORMAT),
        }

        content = self._render_report(
            MONTHLY_REPORT_TEMPLATE,
            context,
            f"Monthly Report — {month_name}",
        )

        filename = MONTHLY_REPORT_PATTERN.format(year=year, month=month)
        report_path = self._reports_dir / filename
        report_path.write_text(content, encoding="utf-8")
        logger.info("Generated monthly report: %s", report_path)
        return report_path
