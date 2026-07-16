"""Project-wide constants for GitHub Streak AI.

Centralizes magic strings, date formats, file patterns, and default values
so they can be changed in one place.
"""

from __future__ import annotations

# ── Directory Names ──────────────────────────────────────────
LOG_DIR = "logs"
REPORTS_DIR = "reports"
TEMPLATES_DIR = "templates"
DASHBOARD_DIR = "dashboard"
DOCS_DIR = "docs"
GITHUB_DIR = ".github"

# ── Date & Time Formats ─────────────────────────────────────
DATE_FORMAT = "%Y-%m-%d"
MONTH_FORMAT = "%Y-%m"
YEAR_FORMAT = "%Y"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%B %d, %Y"  # e.g., "January 15, 2024"

# ── File Patterns ────────────────────────────────────────────
LOG_FILENAME_PATTERN = "{year}/{month:02d}/{year}-{month:02d}-{day:02d}.md"
WEEKLY_REPORT_PATTERN = "week-{week:02d}.md"
MONTHLY_REPORT_PATTERN = "month-{year}-{month:02d}.md"

# ── Template Names ───────────────────────────────────────────
DAILY_LOG_TEMPLATE = "daily_log.md.j2"
WEEKLY_REPORT_TEMPLATE = "weekly_report.md.j2"
MONTHLY_REPORT_TEMPLATE = "monthly_report.md.j2"
DASHBOARD_TEMPLATE = "dashboard.md.j2"

# ── Log Sections ─────────────────────────────────────────────
LOG_SECTIONS = [
    "Goals",
    "Completed Tasks",
    "Study Notes",
    "Coding Notes",
    "Bugs Fixed",
    "Learnings",
    "Tomorrow Plan",
    "AI Summary",
]

# ── Streak Status ────────────────────────────────────────────
STREAK_ACTIVE = "🔥 Active"
STREAK_AT_RISK = "⚠️ At Risk"
STREAK_BROKEN = "❌ Broken"

# ── AI Prompts ───────────────────────────────────────────────
SUMMARY_SYSTEM_PROMPT = (
    "You are a professional technical writer and productivity assistant. "
    "Your job is to convert raw developer notes into clean, well-structured "
    "markdown documentation. Be concise, professional, and actionable. "
    "Preserve all technical details while improving clarity and formatting."
)

WEEKLY_ANALYSIS_SYSTEM_PROMPT = (
    "You are a senior engineering manager reviewing a developer's weekly activity. "
    "Analyze the provided daily logs and generate a comprehensive weekly report "
    "with insights on productivity, learning patterns, and actionable recommendations. "
    "Be encouraging but honest."
)

MONTHLY_INSIGHTS_SYSTEM_PROMPT = (
    "You are a career coach and engineering mentor reviewing a developer's monthly progress. "
    "Analyze the provided data and generate deep insights on growth patterns, skill development, "
    "and strategic recommendations for the next month. Include specific, actionable advice."
)

# ── Dashboard ────────────────────────────────────────────────
PROGRESS_BAR_LENGTH = 20
PROGRESS_BAR_FILLED = "█"
PROGRESS_BAR_EMPTY = "░"

# ── Badge Colors ─────────────────────────────────────────────
BADGE_COLORS = {
    "streak": "ff6b35",
    "logs": "4ecdc4",
    "commits": "45b7d1",
    "hours": "96ceb4",
    "projects": "ffeaa7",
    "technologies": "dda0dd",
}

# ── API ──────────────────────────────────────────────────────
NVIDIA_CHAT_ENDPOINT = "/chat/completions"
DEFAULT_REQUEST_TIMEOUT = 60  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2.0
