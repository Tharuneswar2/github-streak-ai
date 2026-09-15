"""Configuration package for GitHub Streak AI.

Provides centralized settings management via Pydantic and environment variables.
"""

from config.constants import (
    DASHBOARD_DIR,
    DATE_FORMAT,
    LOG_DIR,
    REPORTS_DIR,
    TEMPLATES_DIR,
)
from config.settings import Settings, get_settings

__all__ = [
    "DASHBOARD_DIR",
    "DATE_FORMAT",
    "LOG_DIR",
    "REPORTS_DIR",
    "TEMPLATES_DIR",
    "Settings",
    "get_settings",
]
