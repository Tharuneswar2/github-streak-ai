"""Configuration package for GitHub Streak AI.

Provides centralized settings management via Pydantic and environment variables.
"""

from config.settings import get_settings, Settings
from config.constants import (
    DATE_FORMAT,
    LOG_DIR,
    REPORTS_DIR,
    TEMPLATES_DIR,
    DASHBOARD_DIR,
)

__all__ = [
    "get_settings",
    "Settings",
    "DATE_FORMAT",
    "LOG_DIR",
    "REPORTS_DIR",
    "TEMPLATES_DIR",
    "DASHBOARD_DIR",
]
