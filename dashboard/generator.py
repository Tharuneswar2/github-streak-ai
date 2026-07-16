"""Dashboard README generator.

Creates a professional README.md dashboard with streak stats,
badges, progress bars, recent activity, and project summaries.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from config.constants import (
    DASHBOARD_TEMPLATE,
    PROGRESS_BAR_EMPTY,
    PROGRESS_BAR_FILLED,
    PROGRESS_BAR_LENGTH,
)
from config.settings import Settings, get_settings
from dashboard.badges import BadgeGenerator
from scripts.log_manager import LogManager
from scripts.streak_tracker import StreakTracker

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """Generates the README.md dashboard from project data.

    Combines streak data, log statistics, and badge generation
    into a professional README using Jinja2 templates.

    Example:
        >>> gen = DashboardGenerator()
        >>> path = gen.generate()
        >>> print(f"Dashboard written to: {path}")
    """

    def __init__(
        self,
        settings: Settings | None = None,
        log_manager: LogManager | None = None,
        streak_tracker: StreakTracker | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._log_manager = log_manager or LogManager(self._settings)
        self._streak_tracker = streak_tracker or StreakTracker(self._settings)
        self._badges = BadgeGenerator()

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

    @staticmethod
    def _progress_bar(value: int, maximum: int) -> str:
        """Create a text-based progress bar.

        Args:
            value: Current value.
            maximum: Maximum value.

        Returns:
            Progress bar string like '████████░░░░ 67%'.
        """
        if maximum <= 0:
            return f"{PROGRESS_BAR_EMPTY * PROGRESS_BAR_LENGTH} 0%"
        ratio = min(value / maximum, 1.0)
        filled = int(ratio * PROGRESS_BAR_LENGTH)
        empty = PROGRESS_BAR_LENGTH - filled
        percentage = int(ratio * 100)
        return f"{PROGRESS_BAR_FILLED * filled}{PROGRESS_BAR_EMPTY * empty} {percentage}%"

    def _collect_dashboard_data(self) -> dict[str, Any]:
        """Gather all data needed for the dashboard.

        Returns:
            Dictionary with all dashboard context variables.
        """
        streak_info = self._streak_tracker.get_streak_info()
        total_logs = self._log_manager.get_total_log_count()
        log_dates = self._log_manager.get_log_dates()

        # Estimate study hours from log content
        total_lines = 0
        for log_path in self._log_manager.list_logs():
            try:
                total_lines += len(log_path.read_text(encoding="utf-8").splitlines())
            except OSError:
                continue
        estimated_hours = round(total_lines / 50, 1)

        # Extract technologies from logs (scan last 30 logs)
        technologies: set[str] = set()
        tech_keywords = [
            "python", "javascript", "typescript", "react", "node", "docker",
            "kubernetes", "aws", "sql", "redis", "git", "linux", "rust", "go",
            "java", "fastapi", "django", "flask", "vue", "angular", "terraform",
        ]
        recent_logs = log_dates[-30:] if len(log_dates) > 30 else log_dates
        for d in recent_logs:
            try:
                content = self._log_manager.get_log(d).lower()
                for tech in tech_keywords:
                    if tech in content:
                        technologies.add(tech.title())
            except Exception:
                continue

        # Get recent activity
        recent_activity: list[dict[str, str]] = []
        for d in reversed(log_dates[-5:]):
            recent_activity.append({
                "date": d.isoformat(),
                "display_date": d.strftime("%B %d, %Y"),
                "day": d.strftime("%A"),
            })

        # Generate badges
        badges_md = self._badges.generate_all_badges(
            streak=streak_info["current_streak"],
            logs=total_logs,
            commits=0,
            hours=estimated_hours,
            projects=len(technologies),
        )

        # Progress bars
        today = date.today()
        days_in_year = 366 if today.year % 4 == 0 else 365
        yearly_progress = self._progress_bar(total_logs, days_in_year)
        streak_progress = self._progress_bar(
            streak_info["current_streak"],
            max(streak_info["longest_streak"], 30),
        )

        return {
            "current_streak": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"],
            "streak_status": streak_info["status"],
            "total_logs": total_logs,
            "estimated_hours": estimated_hours,
            "technologies": sorted(technologies),
            "recent_activity": recent_activity,
            "badges": badges_md,
            "yearly_progress": yearly_progress,
            "streak_progress": streak_progress,
            "today_logged": streak_info["today_logged"],
            "generated_date": today.strftime("%Y-%m-%d %H:%M"),
        }

    def generate(self, output_path: Path | None = None) -> Path:
        """Generate the README dashboard.

        Args:
            output_path: Where to write the dashboard. Defaults to project root README.md.

        Returns:
            Path to the generated file.
        """
        output_path = output_path or (self._settings.project_root / "README.md")
        context = self._collect_dashboard_data()

        if self._jinja_env is not None:
            try:
                template = self._jinja_env.get_template(DASHBOARD_TEMPLATE)
                content = template.render(**context)
            except TemplateNotFound:
                logger.warning("Dashboard template not found, using fallback.")
                content = self._fallback_dashboard(context)
        else:
            content = self._fallback_dashboard(context)

        output_path.write_text(content, encoding="utf-8")
        logger.info("Dashboard generated at %s", output_path)
        return output_path

    @staticmethod
    def _fallback_dashboard(ctx: dict[str, Any]) -> str:
        """Generate a dashboard when no template is available."""
        lines = [
            '<div align="center">',
            "",
            "# 🚀 GitHub Streak AI",
            "",
            "*AI-powered daily logging & streak management*",
            "",
            ctx["badges"],
            "",
            "</div>",
            "",
            "---",
            "",
            "## 📊 Dashboard",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| 🔥 Current Streak | **{ctx['current_streak']} days** |",
            f"| 🏆 Longest Streak | **{ctx['longest_streak']} days** |",
            f"| 📝 Total Logs | **{ctx['total_logs']}** |",
            f"| ⏱️ Study Hours | **{ctx['estimated_hours']}h** |",
            f"| 🎯 Status | {ctx['streak_status']} |",
            "",
            "## 📈 Progress",
            "",
            f"**Yearly Logging:** `{ctx['yearly_progress']}`",
            "",
            f"**Streak Progress:** `{ctx['streak_progress']}`",
            "",
        ]

        if ctx["technologies"]:
            lines.extend(["## 🛠️ Technologies", ""])
            tech_badges = " ".join(f"`{t}`" for t in ctx["technologies"])
            lines.extend([tech_badges, ""])

        if ctx["recent_activity"]:
            lines.extend(["## 🕐 Recent Activity", ""])
            for act in ctx["recent_activity"]:
                lines.append(f"- **{act['display_date']}** ({act['day']})")
            lines.append("")

        lines.extend([
            "---",
            "",
            f"*Last updated: {ctx['generated_date']}*  ",
            "*Powered by [GitHub Streak AI](https://github.com/yourusername/github-streak-ai)*",
        ])
        return "\n".join(lines) + "\n"
