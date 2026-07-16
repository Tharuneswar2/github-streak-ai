"""Badge generation using shields.io URLs.

Creates dynamic markdown badge images for the README dashboard.
"""

from __future__ import annotations

from urllib.parse import quote

from config.constants import BADGE_COLORS


class BadgeGenerator:
    """Generates shields.io badge markdown strings.

    Example:
        >>> gen = BadgeGenerator()
        >>> badge = gen.streak_badge(42)
        >>> print(badge)  # ![Streak](https://img.shields.io/badge/...)
    """

    SHIELDS_BASE = "https://img.shields.io/badge"

    @staticmethod
    def _make_badge(label: str, value: str, color: str, logo: str = "") -> str:
        """Create a shields.io badge markdown string.

        Args:
            label: Badge label text.
            value: Badge value text.
            color: Hex color code (without #).
            logo: Optional logo name (e.g., 'github').

        Returns:
            Markdown image string.
        """
        # Shields.io uses dashes for spaces and double underscores for dashes
        safe_label = quote(label.replace("-", "--").replace(" ", "_"))
        safe_value = quote(str(value).replace("-", "--").replace(" ", "_"))
        url = f"https://img.shields.io/badge/{safe_label}-{safe_value}-{color}"
        if logo:
            url += f"?logo={logo}&logoColor=white"
        url += "&style=for-the-badge"
        alt = f"{label}: {value}"
        return f"![{alt}]({url})"

    def streak_badge(self, days: int) -> str:
        """Generate a streak badge."""
        return self._make_badge("🔥 Streak", f"{days} days", BADGE_COLORS["streak"], "fire")

    def logs_badge(self, count: int) -> str:
        """Generate a total logs badge."""
        return self._make_badge("📝 Logs", str(count), BADGE_COLORS["logs"])

    def commits_badge(self, count: int) -> str:
        """Generate a commits badge."""
        return self._make_badge("📊 Commits", str(count), BADGE_COLORS["commits"], "git")

    def hours_badge(self, hours: float) -> str:
        """Generate a study hours badge."""
        return self._make_badge("⏱️ Hours", f"{hours:.1f}h", BADGE_COLORS["hours"])

    def projects_badge(self, count: int) -> str:
        """Generate a projects badge."""
        return self._make_badge("🚀 Projects", str(count), BADGE_COLORS["projects"])

    def tech_badge(self, tech: str) -> str:
        """Generate a technology badge."""
        return self._make_badge(tech, "✓", BADGE_COLORS["technologies"], tech.lower())

    def custom_badge(self, label: str, value: str, color: str = "blue") -> str:
        """Generate a custom badge."""
        return self._make_badge(label, value, color)

    def generate_all_badges(
        self,
        streak: int = 0,
        logs: int = 0,
        commits: int = 0,
        hours: float = 0.0,
        projects: int = 0,
    ) -> str:
        """Generate all standard badges as a single markdown string.

        Args:
            streak: Current streak days.
            logs: Total log count.
            commits: Total commits.
            hours: Study hours.
            projects: Project count.

        Returns:
            Space-separated markdown badges.
        """
        badges = [
            self.streak_badge(streak),
            self.logs_badge(logs),
            self.commits_badge(commits),
            self.hours_badge(hours),
            self.projects_badge(projects),
        ]
        return " ".join(badges)
