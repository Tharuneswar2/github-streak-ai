"""Scripts package for GitHub Streak AI.

Contains core business logic modules:
- ai_client: NVIDIA NIM API integration
- log_manager: Daily log CRUD operations
- report_generator: Weekly and monthly reports
- git_stats: Repository statistics
- streak_tracker: Contribution streak tracking
"""

from scripts.ai_client import NvidiaAIClient
from scripts.log_manager import LogManager
from scripts.report_generator import ReportGenerator
from scripts.git_stats import GitStatsCollector
from scripts.streak_tracker import StreakTracker

__all__ = [
    "NvidiaAIClient",
    "LogManager",
    "ReportGenerator",
    "GitStatsCollector",
    "StreakTracker",
]
